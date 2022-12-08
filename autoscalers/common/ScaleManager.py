import time
import math
from pathlib import Path
import os
from .applications import ApplicationManager
from .Configuration import Configurations


class ScaleManager:
    configurations: Configurations
    metricsGatherer: ApplicationManager
    desiredParallelisms: {str, int}

    def __init__(self, configurations: Configurations, metricsGatherer: ApplicationManager):
        """
        Constructor of the scaleManager. Instantiates a configurations class and a metricsGatherer class.
        :param configurations:
        :param metricsGatherer:
        """
        self.configurations = configurations
        self.desiredParallelisms = {}
        self.metricsGatherer = metricsGatherer
        self.nonreactiveJobmanagerTemplate = "resources/templates/non-reactive-jobmanager-template.yaml"
        self.nonreactiveJobmanagerSavefile = "resources/tmp/jobmanager_from_savepoint.yaml"
        for path in [self.nonreactiveJobmanagerSavefile]:
            directory = Path(path).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Added directory {directory}.")

    def _adaptScalingToExistingResources(self, desiredParallelisms: dict[str, int]) -> dict[str, int]:
        """
        Adapt the desired parallelisms to the available resources.
        :param desiredParallelisms: The per-operator desired parallelisms as a dictionary.
        :return: The per-operator desired parallelisms as a dictionary adapted to the maximum available operators.
        """
        minimum_parallelism = len(desiredParallelisms.keys())
        adaptationFactor = (self.configurations.AVAILABLE_TASKMANAGERS - minimum_parallelism) / (
                    sum(desiredParallelisms.values()) - minimum_parallelism)
        max_parallelism = 0
        max_operator = ""
        for operator, parallelism in desiredParallelisms.items():
            if max_parallelism < parallelism:
                max_parallelism = parallelism
                max_operator = operator
            desiredParallelisms[operator] = 1 + round(adaptationFactor * (parallelism - 1))
        if sum(desiredParallelisms.values()) > self.configurations.AVAILABLE_TASKMANAGERS:
            desiredParallelisms[max_operator] -= 1
        if sum(desiredParallelisms.values()) < self.configurations.AVAILABLE_TASKMANAGERS:
            desiredParallelisms[max_operator] += 1
        return desiredParallelisms

    def _checkForSufficientResources(self, desiredParallelisms: dict[str, int]):
        """
        Check if there are enough TaskManagers to reach the desired parallelism.
        :param desiredParallelisms: The per-operator desired parallelisms as a dictionary.
        :return: True if there are enough TaskManagers for the desired parallelisms, else False.
        """
        totalAvailableTaskManagers = self.configurations.AVAILABLE_TASKMANAGERS
        if self.configurations.USE_FLINK_REACTIVE:
            if max(desiredParallelisms.values()) > totalAvailableTaskManagers:
                print("Insufficient resources for the desired parallelisms.")
                return False
            else:
                return True
        else:
            if sum(desiredParallelisms.values()) > totalAvailableTaskManagers:
                print("Insufficient resources for the desired parallelisms.")
                return False
            else:
                return True

    @staticmethod
    def _enforceMinimumParallelismCondition(desiredParallelisms: dict[str, int]):
        """
        Enforce the condition that each operator must use at least one TaskManager.
        :param desiredParallelisms: The per-operator desired parallelisms as a dictionary.
        :return: None. Dictionaries are mutable in python and changes happen in-place.
        """
        for operator, parallelism in desiredParallelisms.items():
            if parallelism < 1:
                desiredParallelisms[operator] = 1

    def _calculateParallelismIncludingOverprovisioningFactor(self, parallelism: int,
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

    def _addOverprovisioningFactorToDesiredParallelism(self, desiredParallelisms: {str, int},
                                                       overprovisioning_factor: float = None):
        """
        Given the desired parallelism. Calculate the operator's parallelism after adding the overprovisioning_factor.
        :param desiredParallelisms: desired parallelisms.
        :param overprovisioning_factor: overprovisioning_factor to add. Self.configurations.OVERPROVISIONING_FACTOR is
        used when left None.
        """
        for operator in desiredParallelisms:
            parallelism = desiredParallelisms[operator]
            new_parallelism = self._calculateParallelismIncludingOverprovisioningFactor(parallelism,
                                                                                        overprovisioning_factor)
            desiredParallelisms[operator] = new_parallelism

    # Scaling operation
    def performScaleOperations(self, currentParallelisms: {str, int}, desiredParallelisms: {str, int}):
        """
        Perform a scaling operation from current parallelisms to desiredParallelisms.
        If we use Flink-reactive, we scale the amount of taskmanagers to the maximum desired parallelism. If this
        maximum is the same as the current maximum, we do not do anything.
        If we do non use Flink-reactive, we invoke the _performOperatorBasedScaling function, disabling manually
        removing the job and restarting a new one with slot-sharing disabled and parallelisms assigned by
        desiredParallelisms. If currentParallelisms are similar to desired parallelisms, we do not do anything.
        After a scaling operation, we invoke a cooldownPeriod as defined by cooldownPeriod. When undefined, we skip
        the cooldown period.
        :param currentParallelisms: The per-operator current parallelisms
        :param desiredParallelisms: The per-operator desired parallelisms
        :return: None
        """
        parallelismIntersection = [key for key in currentParallelisms if key in desiredParallelisms]
        if not (len(parallelismIntersection) == len(desiredParallelisms) == len(currentParallelisms)):
            raise Exception(f"Parallelism keys do not match: Length of desiredParallelism {desiredParallelisms}, "
                            f"currentParallelisms {currentParallelisms} differ and their intersection: "
                            f"{parallelismIntersection}")

        self._addOverprovisioningFactorToDesiredParallelism(desiredParallelisms)
        self._enforceMinimumParallelismCondition(desiredParallelisms)

        performedScalingOperation = False
        if self.configurations.USE_FLINK_REACTIVE:
            desiredTaskmanagersAmount = max(desiredParallelisms.values())
            currentTaskmanagerAmount = max(currentParallelisms.values())
            if not self._checkForSufficientResources(desiredParallelisms):
                print(f"Not enough resources for desired parallelism of {desiredTaskmanagersAmount}. Setting "
                      f"desiredParallelism to the maximum of {self.configurations.AVAILABLE_TASKMANAGERS} taskmanagers")
                desiredTaskmanagersAmount = self.configurations.AVAILABLE_TASKMANAGERS
            if currentTaskmanagerAmount != desiredTaskmanagersAmount:
                print(f"Performing scaling operation. Scaling from {currentTaskmanagerAmount} to "
                      f"{desiredTaskmanagersAmount}.")
                performedScalingOperation = True
                self.metricsGatherer.kubernetesManager.adaptFlinkTaskmanagersParallelism(desiredTaskmanagersAmount)
        else:
            if not self._checkForSufficientResources(desiredParallelisms):
                if self.configurations.NONREACTIVE_ADJUST_ON_INSUFFICIENT_RESOURCES:
                    desiredParallelisms = self._adaptScalingToExistingResources(desiredParallelisms)
                else:
                    print("Scaling decision ignored due to insufficient TaskManagers.")
                    return
            changeInParallelism = False
            for operator in desiredParallelisms.keys():
                if currentParallelisms[operator] != desiredParallelisms[operator]:
                    changeInParallelism = True
            if changeInParallelism:
                print(f"Performing scaling operation. Scaling from {currentParallelisms} to {desiredParallelisms}.")
                self._performOperatorBasedScaling(currentParallelisms, desiredParallelisms)
                performedScalingOperation = True

        if performedScalingOperation:
            print(f"Performed scaling operation. Entering {self.configurations.COOLDOWN_PERIOD_SECONDS}s "
                  f"cooldown-period.")
            time.sleep(self.configurations.COOLDOWN_PERIOD_SECONDS)

    def _performOperatorBasedScaling(self, currentParallelisms: {str, int}, desiredParallelisms: {str, int}):
        """
        Perform non-reactive operator-based scaling.
        This includes the following steps
        1. Creating and obtain a savepoint.
        2. Scale taskmanagers to the sum of all 'desiredParallelisms'
        3. Construct new jobmanager yaml with updated parallelisms
        4. Delete current jobmanager
        5. Construct new jobmanager
        :param currentParallelisms: The current parallelisms as we know it
        :param desiredParallelisms: The desired parallelisms that we should scale to
        :return:
        """

        # Idea;
        # Trigger savepoint
        #   Wait for savepoint
        # Stop job
        # Trigger savepoint and get Id

        # To do it correctly
        # Stop jobmanager
        # Get trigger id from stop command
        # wait for savepoint to be finished and stop command to be executed
        # continue

        # print("Triggering savepoint")
        # job_id = self.metricsGatherer.jobmanagerManager.getJobId()
        # trigger_id = self.metricsGatherer.jobmanagerManager.triggerSavepointAndGetTriggerId(job_id=job_id)
        # print(f"Triggered savepoint of trigger_id: {trigger_id}")

        # Execute stop request
        job_id = self.metricsGatherer.jobmanagerManager.getJobId()
        print(f"Stopping job {job_id} with a savepoint.")
        stop_request, trigger_id = self.metricsGatherer.jobmanagerManager.sendStopJobRequestAndGetSavePointTriggerId(
            job_id=job_id)
        print(stop_request.json())
        print(f"Triggered savepoint with trigger_id: {trigger_id}")

        # Job stopping is an async operation, we need to query the status before we can continue
        savepointStatus = ""
        savepointPath = ""
        while savepointStatus not in ["COMPLETED", "FAILED"]:
            savepointStatus, savepointPath = self.metricsGatherer.jobmanagerManager\
                .extractSavePointStatusFromSavePointTriggerJSON(job_id=job_id, trigger_id=trigger_id)
            time.sleep(1)
            print(f"Savepoint status: {savepointStatus}")

        if savepointStatus == "FAILED":
            raise Exception("Creating a savepoint failed.")

        if savepointPath == "":
            raise Exception("Unable to fetch path of savepoint.")

        print(f"Savepoint is saved at {savepointPath}")

        # Create new jobmanager configurations file
        self.__createJobmanagerConfigurationFile(desiredParallelisms, savepointPath)

        # Scale taskmanagers if we need new ones
        currentTotalTaskmanagers = sum(currentParallelisms.values())
        desiredTaskmanagers = sum(desiredParallelisms.values())
        if currentTotalTaskmanagers != desiredTaskmanagers:
            self.metricsGatherer.kubernetesManager.adaptFlinkTaskmanagersParallelism(desiredTaskmanagers)

        # Delete jobmanager job
        self.metricsGatherer.kubernetesManager.deleteJobManager()
        # Wait until jobmanager job is terminated
        self.metricsGatherer.kubernetesManager.waitUntilAllJobmanagerJobsAreRemoved()

        # Delete jobmanager service
        # self.metricsGatherer.kubernetesManager.deleteJobManagerService()
        # Wait until jobmanager service is terminated
        # self.metricsGatherer.kubernetesManager.waitUntilAllJobmanagerServicesAreRemoved()

        # Delete jobmanager pod
        self.metricsGatherer.kubernetesManager.deleteJobManagerPod()
        # Wait until jobmanager pod is terminated
        self.metricsGatherer.kubernetesManager.waitUntilAllJobmanagerPodsAreRemoved()

        # Deploy a new job with updated parallelisms
        self.metricsGatherer.kubernetesManager.deployNewJobManager(self.nonreactiveJobmanagerSavefile)

    # Write Jobmanager Configuration File
    def __writeJobmanagerConfigurationFile(self, **kwargs):
        templateFile = open(self.nonreactiveJobmanagerTemplate, "r")
        template = templateFile.read()
        with open(self.nonreactiveJobmanagerSavefile, 'w+') as yfile:
            yfile.write(template.format(**kwargs))

    def __createJobmanagerConfigurationFile(self, desiredParallelisms: {str, int}, savepointPath: str):
        args = ["standalone-job", "--job-classname", self.configurations.NONREACTIVE_JOB,
                "--fromSavepoint", savepointPath, "--slot-sharing", "true"]
        for operator in desiredParallelisms.keys():
            parameter = self.configurations.experimentData.getParallelismParameterOfOperator(operator)
            if parameter:
                args.append(parameter)
                args.append(str(desiredParallelisms[operator]))
        self.__writeJobmanagerConfigurationFile(container=self.configurations.NONREACTIVE_CONTAINER, args=args)
