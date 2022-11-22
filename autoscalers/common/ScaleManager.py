import traceback
import time
import requests


from .metrics import MetricsGatherer
from .Configurations import Configurations
from kubernetes import client, config, utils


class ScaleManager:

    v1 = None
    configurations: Configurations
    metricsGatherer: MetricsGatherer
    desiredParallelisms: {str, int}


    def __init__(self, configurations: Configurations, metricsGatherer: MetricsGatherer):
        self.configurations = configurations
        self.desiredParallelisms = {}
        self.metricsGatherer = metricsGatherer

    # Scaling operation
    def performScaleOperations(self, currentParallelisms: {str, int}, maximumDesiredParallelisms: {str, int},
                               cooldownPeriod: int = None):
        # Scale if current parallelism is different from desired parallelism
        performedScalingOperation = False
        if self.configurations.USE_FLINK_REACTIVE:
            desiredTaskmanagersAmount = max(maximumDesiredParallelisms.values())
            currentTaskmanagerAmount = max(currentParallelisms.values())
            if currentTaskmanagerAmount != desiredTaskmanagersAmount:
                performedScalingOperation = True
                self.__adaptFlinkTaskmanagersParallelism(desiredTaskmanagersAmount)
        else:
            changeInParallelism = False
            for operator in maximumDesiredParallelisms.keys():
                if currentParallelisms[operator] != maximumDesiredParallelisms[operator]:
                    changeInParallelism = True
            if changeInParallelism:
                self._performOperatorBasedScaling(currentParallelisms, maximumDesiredParallelisms)
                performedScalingOperation = True
        if cooldownPeriod and performedScalingOperation:
            print(f"Performed scaling operation. Entering {cooldownPeriod}s cooldown-period.")
            time.sleep(cooldownPeriod)

    # Trigger savepoint and get the required information
    def __triggerSavepointAndGetTriggerId(self, job_id=None):
        """
        Trigger a savepoint and get the corresponding triggerId
        :param job_id: jo_id to trigger savepoint for
        :return: trigger_id of triggeredSavePoint
        """
        if not job_id:
            job_id = self.metricsGatherer.jobmanagerMetricGatherer.getJobId()
        savePoint = requests.post(f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}/savepoints")
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_SAVEPOINT)
        trigger_id = savePoint.json()['request-id']
        return trigger_id

    def __getSavePointTriggerJSON(self, job_id=None, trigger_id=None):
        """
        Get the status of a triggered svapoint. If no trigger_id is given, invoke a savepoint and use that trigger_id
        :param job_id: Job_id to trigger a savepoint for
        :param trigger_id: Trigger_id if savepoint is already triggered.
        :return: Json with all information regarding the trigger
        """
        if not job_id:
            job_id = self.metricsGatherer.jobmanagerMetricGatherer.getJobId()
            trigger_id = self.__triggerSavepointAndGetTriggerId(job_id=job_id)
        if not trigger_id:
            trigger_id = self.__triggerSavepointAndGetTriggerId(job_id=job_id)
        savepoint_json = requests.get(f"http://flink-jobmanager-rest:8081/jobs/{job_id}/savepoints/{trigger_id}").json()
        return savepoint_json

    def __sendStopJobRequest(self, job_id=None):
        """
        Send a stop request to the jobmanager and get the response.
        :param job_id: Job_id to send a stop-request to.
        :return: The response from the server
        """
        if not job_id:
            job_id = self.metricsGatherer.jobmanagerMetricGatherer.getJobId()
        stop_request = requests.post(f"http://flink-jobmanager-rest:8081/jobs/{job_id}/stop")
        return stop_request

    @staticmethod
    def __extractSavePointStatusFromSavePointTriggerJSON(self, savePointTriggerJson):
        status = savePointTriggerJson["status"]["id"]
        return status

    @staticmethod
    def __extractSavePointPathFromSavePointTriggerJSON(self, savePointTriggerJson):
        location = savePointTriggerJson["operation"]["location"]
        return location

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
        with open('jobmanager_from_savepoint.yaml', 'w') as yfile:
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

    # Remove current jobmanager
    @staticmethod
    def __deleteJobManager():
        try:
            _ = client.BatchV1Api().delete_namespaced_job(name="flink-jobmanager", namespace="default",
                                                      pretty=True)
        except:
            print("Error: deleting jobmanager failed.")
            traceback.print_exc()

    @staticmethod
    def __deleteJobManagerPod():
        try:
            # Delete jobmanager pod
            # delete the remaining jobmanager pod
            response = client.CoreV1Api().list_namespaced_pod(namespace="default")
            # find name
            jobmanager_name = None
            for i in response.items:
                if "jobmanager" in i.metadata.name:
                    print("Found jobmanager id: " + str(i.metadata.name))
                    jobmanager_name = i.metadata.name
            # delete pod
            if jobmanager_name is not None:
                _ = client.CoreV1Api().delete_namespaced_pod(name=jobmanager_name, namespace="default")
                print("deleted pod")
            else:
                print("No jobmanager pod found")
        except:
            print("Error: failed deleteing jobmanager pod")
            traceback.print_exc()

    # Set amount of Flink Taskmanagers
    def __adaptFlinkTaskmanagersParallelism(self, new_number_of_taskmanagers):
        try:
            print(f"Scaling total amount of taskmanagers to {new_number_of_taskmanagers}")
            body = {"spec": {"replicas": new_number_of_taskmanagers}}
            api_response = self.v1.patch_namespaced_deployment_scale(
                name="flink-taskmanager", namespace="default", body=body,
                pretty=True)
        except:
            traceback.print_exc()

    def _performOperatorBasedScaling(self, currentParallelisms: {str, int}, desiredParallelisms: {str, int}):
        # Trigger savepoint and get Id
        print("Triggering savepoint")
        job_id = self.metricsGatherer.jobmanagerMetricGatherer.getJobId()
        trigger_id = self.__triggerSavepointAndGetTriggerId(job_id=job_id)
        print("Triggered savepoint of ")
        # Execute stop request
        stop_request = self.__sendStopJobRequest(job_id=job_id)
        print(stop_request)

        # Job stopping is an async operation, we need to query the status before we can continue
        status = None
        statusJson = None
        savepointCompleteStatus = "COMPLETED"
        while status != savepointCompleteStatus:
            statusJson = self.__getSavePointTriggerJSON(job_id=job_id, trigger_id=trigger_id)
            savepointStatus = self.__extractSavePointStatusFromSavePointTriggerJSON(statusJson)
            time.sleep(1)
            print(f"Savepoint status: {savepointStatus}")

        savepointPath = self.__extractSavePointPathFromSavePointTriggerJSON(statusJson)
        print(f"Savepoint Path; {savepointPath}")
        self.__createJobmanagerConfigurationFile(desiredParallelisms, savepointPath)

        # Scale taskmanagers if we need new ones
        currentTotalTaskmanagers = sum(currentParallelisms.values())
        desiredTaskmanagers = sum(currentParallelisms.values())
        if currentTotalTaskmanagers != desiredTaskmanagers:
            self.__adaptFlinkTaskmanagersParallelism(desiredTaskmanagers)

        # Delete jobmanager
        self.__deleteJobManager()
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_DELETE_JOB)

        # Delete jobmanager's pod
        self.__deleteJobManagerPod()
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_DELETE_POD)

        # Deploy a new job with updated parallelisms
        k8s_client = client.ApiClient()
        yaml_file = "jobmanager_from_savepoint.yaml"
        utils.create_from_yaml(k8s_client, yaml_file)
