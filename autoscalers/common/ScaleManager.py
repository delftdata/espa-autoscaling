import time
from .applications import ApplicationManager
from .Configurations import Configurations

JOB_MANAGER_FILE = "jobmanager_from_savepoint.yaml"


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

    # Scaling operation
    def performScaleOperations(self, currentParallelisms: {str, int}, desiredParallelisms: {str, int},
                               cooldownPeriod: int = None):
        """
        Perform a scaling operation from current parallelisms to desiredParallelisms.
        If we use Flink-reactive, we scale the amount of taskmanagers to the maximum desired parallelism. If this
        maximum is the same as the current maximum, we do not do anything.
        If we do non use Flink-reactive, we invoke the _performOperatorBasedScaling function, disabling manually
        removing the job and restarting a new one with slot-sharing disabled and parallelisms assigned by
        desiredParallelisms. If currentParallelisms is simislar to desired parallelisms, we do not do anything.
        After a scaling operation, we invoke a cooldownPeriod as defined by cooldownPeriod. When undefined, we skip
        the cooldown period
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
            return

        for key in currentParallelisms.keys():
            if key not in desiredParallelisms:
                print(
                    f"Key {key} found in  currentParallelisms {currentParallelisms} does not exist in "
                    f"desiredParallelisms {desiredParallelisms}.")
                print(f"Canceling scaling operation")
                return

        for key in desiredParallelisms.keys():
            if key not in currentParallelisms:
                print(
                    f"Key {key} found in desiredParallelisms {desiredParallelisms} does not exist in "
                    f"currentParallelisms {currentParallelisms}.")
                print(f"Canceling scaling operation")
                break

        performedScalingOperation = False
        if self.configurations.USE_FLINK_REACTIVE:
            desiredTaskmanagersAmount = max(desiredParallelisms.values())
            currentTaskmanagerAmount = max(currentParallelisms.values())
            if currentTaskmanagerAmount != desiredTaskmanagersAmount:
                performedScalingOperation = True
                self.metricsGatherer.kubernetesManager.adaptFlinkTaskmanagersParallelism(desiredTaskmanagersAmount)
        else:
            changeInParallelism = False
            for operator in desiredParallelisms.keys():
                if currentParallelisms[operator] != desiredParallelisms[operator]:
                    changeInParallelism = True
            if changeInParallelism:
                self._performOperatorBasedScaling(currentParallelisms, desiredParallelisms)
                performedScalingOperation = True
        if cooldownPeriod and performedScalingOperation:
            print(f"Performed scaling operation. Entering {cooldownPeriod}s cooldown-period.")
            time.sleep(cooldownPeriod)

    def _performOperatorBasedScaling(self, currentParallelisms: {str, int}, desiredParallelisms: {str, int}):
        """
        Perform non-reative operator-based scaling.
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
        # Trigger savepoint and get Id
        print("Triggering savepoint")
        job_id = self.metricsGatherer.jobmanagerManager.getJobId()
        trigger_id = self.metricsGatherer.jobmanagerManager.triggerSavepointAndGetTriggerId(job_id=job_id)
        print(f"Triggered savepoint of trigger_id: {trigger_id}")
        # Execute stop request
        stop_request = self.metricsGatherer.jobmanagerManager.sendStopJobRequest(job_id=job_id)
        print(stop_request.json())

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
                return

        savepointPath = self.metricsGatherer.jobmanagerManager.extractSavePointPathFromSavePointTriggerJSON(
            job_id=job_id, trigger_id=trigger_id
        )
        print(f"Savepoint Path; {savepointPath}")
        if not savepointPath:
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
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_DELETE_JOB)

        # Delete jobmanager's pod
        self.metricsGatherer.kubernetesManager.deleteJobManagerPod()
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_DELETE_POD)

        # Deploy a new job with updated parallelisms
        self.metricsGatherer.kubernetesManager.deployNewJobManager(JOB_MANAGER_FILE)

    # Write Jobmanager Configuration File
    def __writeJobmanagerConfigurationFile(**kwargs):
        template = """
            apiVersion: batch/v1
            kind: Job
            metadata:
              name: flink-jobmanager
            spec:
              template:
                metadata:
                  annotations:
                    prometheus.io/port: '9249'
                    ververica.com/scrape_every_2s: 'true'
                  labels:
                    app: flink
                    component: jobmanager
                spec:
                  restartPolicy: OnFailure
                  containers:
                    - name: jobmanager
                      image: {container}
                      imagePullPolicy: Always
                      env:
                      args: {args}
                      ports:
                        - containerPort: 6123
                          name: rpc
                        - containerPort: 6124
                          name: blob-server
                        - containerPort: 8081
                          name: webui
                      livenessProbe:
                        tcpSocket:
                          port: 6123
                        initialDelaySeconds: 30
                        periodSeconds: 60
                      volumeMounts:
                        - name: flink-config-volume
                          mountPath: /opt/flink/conf
                        - name: my-pvc-nfs
                          mountPath: /opt/flink/savepoints
                      securityContext:
                        runAsUser: 0  # refers to user _flink_ from official flink image, change if necessary
                  volumes:
                    - name: flink-config-volume
                      configMap:
                        name: flink-config
                        items:
                          - key: flink-conf.yaml
                            path: flink-conf.yaml
                          - key: log4j-console.properties
                            path: log4j-console.properties
                    - name: my-pvc-nfs
                      persistentVolumeClaim:
                        claimName: nfs """
        with open(JOB_MANAGER_FILE, 'w') as yfile:
            yfile.write(template.format(**kwargs))

    @staticmethod
    def __getParamOfOperator(operator, printError=True):
        operator_param_Mapper = {
            # Query 1
            "Source:_BidsSource": "--p-source",
            "Mapper": "--p-map",
            "LatencySink": "--p-sink",
            # Query 3
            "Source:_auctionsSource": "--p-auction-source",
            "Source:_personSource": "--p-person-source",
            "Incrementaljoin": "--p-join",
            # Query 11
            # "Source:_BidsSource": "--p-source",
            "SessionWindow____DummyLatencySink": "--p-window",
        }

        if operator in operator_param_Mapper.keys():
            return operator_param_Mapper[operator]
        else:
            if printError:
                print(f"Error: could not retrieve operator '{operator}' from operator_param_mapper "
                      f"'{operator_param_Mapper}'")

    def __createJobmanagerConfigurationFile(self, desiredParallelisms: {str, int}, savepointPath: str):
        args = ["standalone-job", "--job-classname", self.configurations.NONREACTIVE_JOB, "--fromSavepoint",
                savepointPath]
        for operator in desiredParallelisms.keys():
            parameter = self.__getParamOfOperator(operator)
            if parameter:
                args.append(parameter)
                args.append(desiredParallelisms[operator])
        self.__writeJobmanagerConfigurationFile(container=self.configurations.NONREACTIVE_CONTAINER, args=args)

