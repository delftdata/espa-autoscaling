import time
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
        self.adaptationMode = True          # We should provide this as a configuration option 
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
        adaptationFactor = (self.configurations.MAX_PARALLELISM - minimum_parallelism)/(sum(desiredParallelisms.values()) - minimum_parallelism)
        max_parallelism = 0
        max_operator = ""
        for operator, parallelism in desiredParallelisms.items():
            if max_parallelism < parallelism:
                max_parallelism = parallelism
                max_operator = operator
            desiredParallelisms[operator] = 1 + round(adaptationFactor * (parallelism - 1))
        if sum(desiredParallelisms.values()) > self.configurations.MAX_PARALLELISM:
            desiredParallelisms[max_operator] -= 1 
        if sum(desiredParallelisms.values()) < self.configurations.MAX_PARALLELISM:
            desiredParallelisms[max_operator] += 1
        return desiredParallelisms

    def _checkForSufficientResources(self, flinkReactive: bool, desiredParallelisms: dict[str, int]):
        """
        Check if there are enough TaskManagers to reach the desired parallelism.
        :param flinkReactive: If true, signals that flink is running in reactive mode. False for non-reactive.
        :param desiredParallelisms: The per-operator desired parallelisms as a dictionary.
        :return: True if there are enough TaskManagers for the desired parallelisms, else False.
        """
        totalAvailableTaskManagers = self.configurations.MAX_PARALLELISM
        if flinkReactive:
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

    
    def _enforceMinimumParallelismCondition(self, desiredParallelisms: dict[str, int]):
        """
        Enforce the condition that each operator must use at least one TaskManager.
        :param desiredParallelisms: The per-operator desired parallelisms as a dictionary.
        :return: None. Dictionaries are mutable in python and changes happen in-place.
        """
        for operator, parallelism in desiredParallelisms.items():
            if parallelism < 1:
                desiredParallelisms[operator] = 1



    # Scaling operation
    def performScaleOperations(self, currentParallelisms: {str, int}, desiredParallelisms: {str, int},
                               cooldownPeriod: int = None):
        """
        Perform a scaling operation from current parallelisms to desiredParallelisms.
        If we use Flink-reactive, we scale the amount of taskmanagers to the maximum desired parallelism. If this
        maximum is the same as the current maximum, we do not do anything.
        If we do non use Flink-reactive, we invoke the _performOperatorBasedScaling function, disabling manually
        removing the job and restarting a new one with slot-sharing disabled and parallelisms assigned by
        desiredParallelisms. If currentParallelisms are similar to desired parallelisms, we do not do anything.
        After a scaling operation, we invoke a cooldownPeriod as defined by cooldownPeriod. When undefined, we skip
        the cooldown period.
        :param currentParallelisms: The per-operator current parellelisms
        :param desiredParallelisms: The per-operator desired parallelisms
        :param cooldownPeriod: Optional cooldownperiod to be invoked after a scaling operation happens.
        :return: None
        """

        # Scale if current parallelism is different from desired parallelism
        # Todo, make shorter using intersection
        if len(currentParallelisms) != len(desiredParallelisms):
            print(f"Lenght of currentParallelisms {currentParallelisms} is not the same as desiredParallelisms"
                  f" {desiredParallelisms}.")
            print(f"Canceling scaling operation")
            # Here we can cancel. But maybe we should fail?
            return

        for key in currentParallelisms.keys():
            if key not in desiredParallelisms:
                print(
                    f"Key {key} found in  currentParallelisms {currentParallelisms} does not exist in "
                    f"desiredParallelisms {desiredParallelisms}.")
                print(f"Canceling scaling operation")
                # Same
                return

        for key in desiredParallelisms.keys():
            if key not in currentParallelisms:
                print(
                    f"Key {key} found in desiredParallelisms {desiredParallelisms} does not exist in "
                    f"currentParallelisms {currentParallelisms}.")
                print(f"Canceling scaling operation")
                # Same
                break

        self._enforceMinimumParallelismCondition(desiredParallelisms)

        performedScalingOperation = False
        if self.configurations.USE_FLINK_REACTIVE:
            desiredTaskmanagersAmount = max(desiredParallelisms.values())
            currentTaskmanagerAmount = max(currentParallelisms.values())
            if not self._checkForSufficientResources(True, desiredParallelisms):
                desiredTaskmanagersAmount = self.configurations.MAX_PARALLELISM
            if currentTaskmanagerAmount != desiredTaskmanagersAmount:
                performedScalingOperation = True
                self.metricsGatherer.kubernetesManager.adaptFlinkTaskmanagersParallelism(desiredTaskmanagersAmount)
        else:
            if not self._checkForSufficientResources:
                if self.adaptationMode:
                    desiredParallelisms = self._adaptScalingToExistingResources(desiredParallelisms)
                    changeInParallelism = False
                    for operator in desiredParallelisms.keys():
                        if currentParallelisms[operator] != desiredParallelisms[operator]:
                            changeInParallelism = True
                    if changeInParallelism:
                        self._performOperatorBasedScaling(currentParallelisms, desiredParallelisms)
                        performedScalingOperation = True
                else:
                    print("Scaling decision ignored due to insufficient TaskManagers.")
        if cooldownPeriod and performedScalingOperation:
            print(f"Performed scaling operation. Entering {cooldownPeriod}s cooldown-period.")
            time.sleep(cooldownPeriod)

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
        stop_request, trigger_id = self.metricsGatherer.jobmanagerManager.sendStopJobRequestAndGetSavePointTriggerId(job_id=job_id)
        print(stop_request.json())
        print(f"Triggered savepoint with trigger_id: {trigger_id}")

        # Job stopping is an async operation, we need to query the status before we can continue
        savepointCompleteStatus = "COMPLETED"
        savepointStatus = ""
        timeout = self.configurations.NONREACTIVE_SAVEPOINT_TIMEOUT_TIME_SECONDS
        while savepointStatus != savepointCompleteStatus:
            savepointStatus = self.metricsGatherer.jobmanagerManager.extractSavePointStatusFromSavePointTriggerJSON(
                job_id=job_id, trigger_id=trigger_id
            )
            time.sleep(1)
            timeout -= 1
            print(f"Savepoint status: {savepointStatus}")
            if timeout <= 0:
                print("Timeout for savepoint to complete exceeded.")
                print("Canceling scaling operation")
                # Do we need this? We can't really cancel the scaling operation. After we stop the job we cannot continue. 
                # If the savepoint fails, we should cancel the job and restart from a checkpoint. This is out of scope for us, therefore we should just stop execution.
                return

        savepointPath = self.metricsGatherer.jobmanagerManager.extractSavePointPathFromSavePointTriggerJSON(
            job_id=job_id, trigger_id=trigger_id
        )
        print(f"Savepoint Path; {savepointPath}")
        if not savepointPath:
            # Here the same!
            print("Canceling scaling operation, as savepoint path could not be found.")
            return

        # Create new jobmanager configurations file
        self.__createJobmanagerConfigurationFile(desiredParallelisms, savepointPath)

        # Scale taskmanagers if we need new ones
        currentTotalTaskmanagers = sum(currentParallelisms.values())
        desiredTaskmanagers = sum(currentParallelisms.values())
        if currentTotalTaskmanagers != desiredTaskmanagers:
            self.metricsGatherer.kubernetesManager.adaptFlinkTaskmanagersParallelism()(desiredTaskmanagers)

        # Delete jobmanager
        self.metricsGatherer.kubernetesManager.deleteJobManager()
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_DELETE_JOB_SECONDS)

        # Delete jobmanager's pod
        self.metricsGatherer.kubernetesManager.deleteJobManagerPod()
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_DELETE_POD_SECONDS)

        # Deploy a new job with updated parallelisms
        self.metricsGatherer.kubernetesManager.deployNewJobManager(self.nonreactiveJobmanagerSavefile)

    # Write Jobmanager Configuration File
    def __writeJobmanagerConfigurationFile(self, **kwargs):
        templateFile = open(self.nonreactiveJobmanagerTemplate, "r")
        template = templateFile.read()
        print(template)
        with open(self.nonreactiveJobmanagerSavefile, 'w+') as yfile:
            yfile.write(template.format(**kwargs))

    def __createJobmanagerConfigurationFile(self, desiredParallelisms: {str, int}, savepointPath: str):
        args = ["standalone-job", "--job-classname", self.configurations.NONREACTIVE_JOB, "--fromSavepoint",
                savepointPath]
        for operator in desiredParallelisms.keys():
            parameter = self.configurations.experimentData.getParallelismParameterOfOperator(operator)
            if parameter:
                args.append(parameter)
                args.append(str(desiredParallelisms[operator]))
        self.__writeJobmanagerConfigurationFile(container=self.configurations.NONREACTIVE_CONTAINER, args=args)

