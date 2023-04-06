import time
import math
from pathlib import Path
import os
from .applications import ApplicationManager
from .Configuration import Configurations


class ScaleManager:
    configurations: Configurations
    metrics_gatherer: ApplicationManager
    desired_parallelisms: {str, int}

    def __init__(self, configurations: Configurations, metricsGatherer: ApplicationManager):
        """
        Constructor of the scaleManager. Instantiates a configurations class and a metricsGatherer class.
        :param configurations:
        :param metricsGatherer:
        """
        self.configurations = configurations
        self.desired_parallelisms = {}
        self.metrics_gatherer = metricsGatherer
        self.nonreactive_jobmanager_template = "resources/templates/non-reactive-jobmanager-template.yaml"
        self.nonreactive_jobmanager_savefile = "resources/tmp/jobmanager_from_savepoint.yaml"
        for path in [self.nonreactive_jobmanager_savefile]:
            directory = Path(path).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Added directory {directory}.")

    def _adapt_scaling_to_existing_resources(self, desired_parallelisms: dict[str, int]) -> dict[str, int]:
        """
        Adapt the desired parallelisms to the available resources.
        :param desired_parallelisms: The per-operator desired parallelisms as a dictionary.
        :return: The per-operator desired parallelisms as a dictionary adapted to the maximum available operators.
        """
        minimum_parallelism = len(desired_parallelisms.keys())
        adaptation_factor = (self.configurations.AVAILABLE_TASKMANAGERS - minimum_parallelism) / (
                sum(desired_parallelisms.values()) - minimum_parallelism)
        max_parallelism = 0
        max_operator = ""
        for operator, parallelism in desired_parallelisms.items():
            if max_parallelism < parallelism:
                max_parallelism = parallelism
                max_operator = operator
            desired_parallelisms[operator] = 1 + round(adaptation_factor * (parallelism - 1))
        if sum(desired_parallelisms.values()) > self.configurations.AVAILABLE_TASKMANAGERS:
            desired_parallelisms[max_operator] -= 1
        if sum(desired_parallelisms.values()) < self.configurations.AVAILABLE_TASKMANAGERS:
            desired_parallelisms[max_operator] += 1
        return desired_parallelisms

    def _check_for_sufficient_resources(self, desired_parallelisms: dict[str, int]) -> bool:
        """
        Check if there are enough TaskManagers to reach the desired parallelism.
        :param desired_parallelisms: The per-operator desired parallelisms as a dictionary.
        :return: True if there are enough TaskManagers for the desired parallelisms, else False.
        """
        total_available_task_managers = self.configurations.AVAILABLE_TASKMANAGERS
        if self.configurations.USE_FLINK_REACTIVE:
            if max(desired_parallelisms.values()) > total_available_task_managers:
                print("Insufficient resources for the desired parallelisms.")
                return False
            else:
                return True
        else:
            if sum(desired_parallelisms.values()) > total_available_task_managers:
                print("Insufficient resources for the desired parallelisms.")
                return False
            else:
                return True

    def _enforce_maximum_parallelism_increase_condition(self, desired_parallelisms: dict[str, int],
                                                        current_parallelisms: dict[str, int]) -> None:
        """
        Method enforces a maximum parallelism increase per operator, to accommodate the underlying cluster configuration.
        This method assumes the same keys in desired_parallelisms and current_parallelisms
        :param desired_parallelisms: Dictionary containing a mapping between operators and their desired parallelism.
        :param current_parallelisms: Dictionary containing a mapping between operators and their current parallelism.
        :return: None. DesiredParallelisms is adapted to have a maximum increase of self.configurations.MAXIMUM_PARALLELISM_INCREASE.
        """
        maximum_parallelism_increase = self.configurations.MAXIMUM_PARALLELISM_INCREASE
        for operator, current_parallelism in current_parallelisms.items():
            maximum_parallelism = current_parallelism + maximum_parallelism_increase
            desired_parallelism = desired_parallelisms[operator]
            desired_parallelisms[operator] = min(maximum_parallelism, desired_parallelism)


    @staticmethod
    def _enforce_minimum_parallelism_condition(desired_parallelisms: dict[str, int]) -> None:
        """
        Enforce the condition that each operator must use at least one TaskManager.
        :param desired_parallelisms: The per-operator desired parallelisms as a dictionary.
        :return: None. Dictionaries are mutable in python and changes happen in-place.
        """
        for operator, parallelism in desired_parallelisms.items():
            if parallelism < 1:
                desired_parallelisms[operator] = 1

    def _calculate_parallelism_including_overprovisioning_factor(self, parallelism: int,
                                                                 overprovisioning_factor: float = None) -> int:
        """
        Calculate the parallelism of an operator after adding the overprovisioning_factor.
        :param parallelism: Initial parallelism without adding the overprovisioning_factor
        :param overprovisioning_factor: overprovisioning-factor to multiply parallelism with. Is set to
        self.configurations.OVERPROVISIONING_FACTOR if left None;
        :return: parallelism including overprovisioning_factor
        """
        if not overprovisioning_factor:
            overprovisioning_factor = self.configurations.OVERPROVISIONING_FACTOR
        return math.ceil(parallelism * overprovisioning_factor)

    def _add_overprovisioning_factor_to_desired_parallelism(self, desired_parallelisms: {str, int},
                                                            overprovisioning_factor: float = None) -> None:
        """
        Given the desired parallelism. Calculate the operator's parallelism after adding the overprovisioning_factor.
        :param: desired_parallelisms: desired parallelisms.
        :param: overprovisioning_factor: overprovisioning_factor to add. Self.configurations.OVERPROVISIONING_FACTOR is
        used when left None.
        """
        for operator in desired_parallelisms:
            parallelism = desired_parallelisms[operator]
            new_parallelism = self._calculate_parallelism_including_overprovisioning_factor(parallelism,
                                                                                            overprovisioning_factor)
            desired_parallelisms[operator] = new_parallelism

    # Scaling operation
    def perform_scale_operations(self, current_parallelisms: {str, int}, desired_parallelisms: {str, int}) -> None:
        """
        Perform a scaling operation from current parallelisms to desiredParallelisms.
        If we use Flink-reactive, we scale the amount of taskmanagers to the maximum desired parallelism. If this
        maximum is the same as the current maximum, we do not do anything.
        If we do non use Flink-reactive, we invoke the _performOperatorBasedScaling function, disabling manually
        removing the job and restarting a new one with slot-sharing disabled and parallelisms assigned by
        desiredParallelisms. If currentParallelisms are similar to desired parallelisms, we do not do anything.
        After a scaling operation, we invoke a cooldownPeriod as defined by cooldownPeriod. When undefined, we skip
        the cooldown period.
        :param current_parallelisms: The per-operator current parallelisms
        :param desired_parallelisms: The per-operator desired parallelisms
        :return: None
        """
        parallelism_intersection = [key for key in current_parallelisms if key in desired_parallelisms]
        if not (len(parallelism_intersection) == len(desired_parallelisms) == len(current_parallelisms)):
            raise Exception(f"Parallelism keys do not match: Length of desiredParallelism {desired_parallelisms}, "
                            f"currentParallelisms {current_parallelisms} differ and their intersection: "
                            f"{parallelism_intersection}")


        # Add the overprovisioning factor to the desired parallelisms
        self._add_overprovisioning_factor_to_desired_parallelism(desired_parallelisms)

        # Enforce the parallelism of an operator is only increased by the provided maximum parallelism increase
        self._enforce_maximum_parallelism_increase_condition(desired_parallelisms, current_parallelisms)

        # Enforce the parallelism of each operator is always larger than 0
        self._enforce_minimum_parallelism_condition(desired_parallelisms)

        performed_scaling_operation = False

        # If we use Flink reactive
        if self.configurations.USE_FLINK_REACTIVE:

            # Find maximum parallelism of our desired parallelisms
            desired_taskmanagers_amount = max(desired_parallelisms.values())
            # find current parallelism
            current_taskmanager_amount = max(current_parallelisms.values())

            # If not enough resources
            if not self._check_for_sufficient_resources(desired_parallelisms):
                print(f"Not enough resources for desired parallelism of {desired_taskmanagers_amount}. Setting "
                      f"desiredParallelism to the maximum of {self.configurations.AVAILABLE_TASKMANAGERS} taskmanagers")
                # Set desired parallelism to max available taskmanagers
                desired_taskmanagers_amount = self.configurations.AVAILABLE_TASKMANAGERS
            # If the current amount of taskmanagers is not the amount of taskmanagers we desire
            if current_taskmanager_amount != desired_taskmanagers_amount:
                print(f"Performing scaling operation. Scaling from {current_taskmanager_amount} to "
                      f"{desired_taskmanagers_amount}.")
                # Remember that we perform a scaling operator and scale the amount of taskmanagers to desired_taskmanagers_amount
                performed_scaling_operation = True
                self.metrics_gatherer.kubernetesManager.adapt_flink_taskmanagers_parallelism(desired_taskmanagers_amount)
        # If we do not use flink reactive, we do non-reactive scaling
        else:
            # If not enough resources for our desired parallelism
            if not self._check_for_sufficient_resources(desired_parallelisms):
                # If we adjust the amount of resources to the available taskmanagers (instead of returning)
                if self.configurations.NONREACTIVE_ADJUST_ON_INSUFFICIENT_RESOURCES:
                    # Adjust desired_parallelism to available resources
                    desired_parallelisms = self._adapt_scaling_to_existing_resources(desired_parallelisms)
                else:
                    # Else, we return as we do not wish to adjust and the scaling operation is not possible
                    print("Scaling decision ignored due to insufficient TaskManagers.")
                    return

            # Determine whether any of the parallelisms changed
            change_in_parallelism = False
            for operator in desired_parallelisms.keys():
                if current_parallelisms[operator] != desired_parallelisms[operator]:
                    change_in_parallelism = True
            # If any of the operator's parallelism changed
            if change_in_parallelism:
                # perform non-reactive scaling operation
                print(f"Performing scaling operation. Scaling from {current_parallelisms} to {desired_parallelisms}.")
                self._perform_operator_based_scaling(current_parallelisms, desired_parallelisms)
                # Remember that we executed a scaling operation
                performed_scaling_operation = True

        # If we performed a scaling operation, execute the cooldown period
        if performed_scaling_operation:
            print(f"Performed scaling operation. Entering {self.configurations.COOLDOWN_PERIOD_SECONDS}s "
                  f"cooldown-period.")
            time.sleep(self.configurations.COOLDOWN_PERIOD_SECONDS)

    def _perform_operator_based_scaling(self, current_parallelisms: {str, int}, desired_parallelisms: {str, int}) -> None:
        """
        Perform non-reactive operator-based scaling.
        This includes the following steps
        1. Creating and obtain a savepoint.
        2. Scale taskmanagers to the sum of all 'desiredParallelisms'
        3. Construct new jobmanager yaml with updated parallelisms
        4. Delete current jobmanager
        5. Construct new jobmanager
        :param current_parallelisms: The current parallelisms as we know it
        :param desired_parallelisms: The desired parallelisms that we should scale to
        :return: None
        """

        # Execute stop request. This will stop the job and trigger a savepoint.
        job_id = self.metrics_gatherer.jobmanagerManager.getJobId()
        print(f"Stopping job {job_id} with a savepoint.")
        stop_request, trigger_id = self.metrics_gatherer.jobmanagerManager.sendStopJobRequestAndGetSavePointTriggerId(job_id=job_id)
        print(f"Triggered savepoint with trigger_id: {trigger_id}")

        # Job stopping is an async operation, we need to query the status before we can continue.
        # Keep checking jobstatus until it is COMPLETED and a savepoint_path is provided
        savepoint_status = ""
        savepoint_path = ""
        while savepoint_status not in ["COMPLETED", "FAILED"]:
            savepoint_status, savepoint_path = self.metrics_gatherer.jobmanagerManager\
                .extractSavePointStatusFromSavePointTriggerJSON(job_id=job_id, trigger_id=trigger_id)
            time.sleep(1)
            print(f"Savepoint status: {savepoint_status}")

        # If savepoint failed, throw an exception
        if savepoint_status == "FAILED":
            raise Exception("Creating a savepoint failed.")

        # If savepoint path is not available, throw an exception
        if savepoint_path == "":
            raise Exception("Unable to fetch path of savepoint.")

        print(f"Savepoint is saved at {savepoint_path}")

        # Create new jobmanager configurations file
        self.__create_jobmanager_configuration_file(desired_parallelisms, savepoint_path)

        # Delete jobmanager job
        self.metrics_gatherer.kubernetesManager.delete_jobmanager()
        # Wait until jobmanager job is terminated
        self.metrics_gatherer.kubernetesManager.wait_until_all_jobmanager_jobs_are_removed()

        # Delete jobmanager service (disabled)
        # self.metricsGatherer.kubernetesManager.deleteJobManagerService()
        # Wait until jobmanager service is terminated
        # self.metricsGatherer.kubernetesManager.waitUntilAllJobmanagerServicesAreRemoved()

        # Delete jobmanager pod
        self.metrics_gatherer.kubernetesManager.delete_jobmanager_pod()
        # Wait until jobmanager pod is terminated
        self.metrics_gatherer.kubernetesManager.wait_until_all_jobmanager_pods_are_removed()

        # Scale taskmanagers if we need new ones
        current_total_taskmanagers = sum(current_parallelisms.values())
        desired_taskmanagers = sum(desired_parallelisms.values())
        if current_total_taskmanagers != desired_taskmanagers:
            self.metrics_gatherer.kubernetesManager.adapt_flink_taskmanagers_parallelism(desired_taskmanagers)

        self.metrics_gatherer.kubernetesManager.wait_until_all_taskmanagers_are_running()

        # Deploy a new job with updated parallelisms
        self.metrics_gatherer.kubernetesManager.deploy_new_jobmanager(self.nonreactive_jobmanager_savefile)

    # Write Jobmanager Configuration File
    def __write_jobmanager_configuration_file(self, **kwargs) -> None:
        """
        Read the jobmanager_template, insert the provided parameters and save it to file.
        :param kwargs: Parameters provided to be inserted as parameters in the template
        :return: None
        """
        template_file = open(self.nonreactive_jobmanager_template, "r")
        template = template_file.read()
        with open(self.nonreactive_jobmanager_savefile, 'w+') as yfile:
            yfile.write(template.format(**kwargs))


    def __create_jobmanager_configuration_file(self, desired_parallelisms: {str, int}, savepoint_path: str) -> None:
        """
        Create a jobmanager configuration file with the newly provided desired_parallelisms and save it to savepoint_path
        :param desired_parallelisms: Parallelisms of new topology.
        :param savepoint_path: Location where to save the new jobmanager configuration file.
        :return: None
        """
        args = ["standalone-job", "--job-classname", self.configurations.NONREACTIVE_JOB,
                "--fromSavepoint", savepoint_path, "--slot-sharing", "true"]
        for operator in desired_parallelisms.keys():
            parameter = self.configurations.experimentData.get_parallelism_parameter_of_operator(operator)
            if parameter:
                args.append(parameter)
                args.append(str(desired_parallelisms[operator]))
        self.__write_jobmanager_configuration_file(container=self.configurations.NONREACTIVE_CONTAINER, args=args)
