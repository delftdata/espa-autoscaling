import json
import traceback
import time
import requests

from . import MetricsGatherer
from .Configurations import Configurations


class ScaleManager:

    v1 = None
    configurations: Configurations
    metricsGatherer: MetricsGatherer
    desiredParallelisms: {str, int}

    def __init__(self, configurations: Configurations, metricsGatherer: MetricsGatherer):
        self.configurations = configurations
        self.desiredParallelisms = {}
        self.metricsGatherer = metricsGatherer


    def __scaleOperator(self, operator: str, desiredParallelism):
        """
        TODO: implement operator-based scaling
        Perform a scaling operator for the operator.
        The desiredParallelism is set between [MIN_TASKMANAGERS, MAX_PARALLELISM]
        :param operator: Operator to scale
        :param desiredParallelism: Operator to scale to.
        :return: None
        """
        desiredParallelism = max(self.configurations.MIN_PARALLELISM, desiredParallelism)
        desiredParallelism = min(self.configurations.MAX_PARALLELISM, desiredParallelism)
        self.desiredParallelisms[operator] = desiredParallelism
        print(f"TODO: Scale operator '{operator}' to parallelism '{desiredParallelism}'. ")


    def __adaptFlinkReactiveTaskmanagers(self, new_number_of_taskmanagers):
        if not self.configurations.USE_FLINK_REACTIVE:
            print(f"Error: trying to scale taskmanagers with disabled Flink Reactive. Returning.")
            return

        try:
            print(f"Scaling total amount of taskmanagers to {new_number_of_taskmanagers}")
            body = {"spec": {"replicas": new_number_of_taskmanagers}}
            api_response = self.v1.patch_namespaced_deployment_scale(
                name="flink-taskmanager", namespace="default", body=body,
                pretty=True)
        except:
            traceback.print_exc()

    def performScaleOperations(self, currentParallelisms: {str, int}, maximumDesiredParallelisms: {str, int},
                               cooldownPeriod: int = None):
        # Scale if current parallelism is different from desired parallelism
        performedScalingOperation = False
        if self.configurations.USE_FLINK_REACTIVE:
            desiredTaskmanagersAmount = max(maximumDesiredParallelisms.values())
            currentTaskmanagerAmount = max(currentParallelisms.values())
            if currentTaskmanagerAmount != desiredTaskmanagersAmount:
                performedScalingOperation = True
                self.__adaptFlinkReactiveTaskmanagers(desiredTaskmanagersAmount)
        else:
            for operator in maximumDesiredParallelisms.keys():
                currentParallelism = currentParallelisms[operator]
                desiredParallelism = maximumDesiredParallelisms[operator]
                if currentParallelism != desiredParallelism:
                    performedScalingOperation = True
                    self.__scaleOperator(operator, desiredParallelism)

        if cooldownPeriod and performedScalingOperation:
            print(f"Performed scaling operation. Entering {cooldownPeriod}s cooldown-period.")
            time.sleep(cooldownPeriod)


    # Non-reactive scaling functionality
    def __triggerSavepointAndGetTriggerId(self, job_id=None):
        """
        Trigger a savepoint and get the corresponding triggerId
        :param job_id: jo_id to trigger savepoint for
        :return: trigger_id of triggeredSavePoint
        """
        if not job_id:
            job_id = self.__getJobId()
        savePoint = requests.post(f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}/savepoints")
        time.sleep(self.configurations.NONREACTIVE_TIME_AFTER_SAVEPOINT)
        trigger_id = savePoint.json()['request-id']
        return trigger_id

    def triggerSavepointAndGetInformation(self, job_id=None, trigger_id=None):
        """
        Trigger a savepoint and get the corresponding information in json format.
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


    def sendStopJobRequest(self, job_id=None):
        """
        Send a stop request to the jobmanager and get the response.
        :param job_id: Job_id to send a stop-request to.
        :return: The response from the server
        """
        if not job_id:
            job_id = self..jobmanagerMetricGatherer.getJobId()
        stop_request = requests.post(f"http://flink-jobmanager-rest:8081/jobs/{job_id}/stop")
        return stop_request

    SAVEPOINT_IN_PROGRESS_STATUS = "IN_PROGRESS"
    SAVEPOINT_COMPLETED_STATUS = "COMPLETED"

    def ds2_operator_scale_operations(self):
        # Set savepoint
        savepoint_json = self.triggerSavepointAndGetInformation()
        print(json.dumps(savepoint_json.json(), indent=4))
        savepoint_path = savepoint_json.json()["operation"]["location"]

        # Execute stop request
        stop_request = self.sendStopJobRequest()
        print(stop_request)

        # Job stopping is an async operation, we need to query the status before we can continue
        status = self.SAVEPOINT_IN_PROGRESS_STATUS
        while status == self.SAVEPOINT_IN_PROGRESS_STATUS:
            r = requests.get(f'http://flink-jobmanager-rest:8081/jobs/{job_id}/savepoints/{trigger_id}')
            print("REQ2 RES - CHECKING:")
            print(r.json())
            status = r.json()["status"]["id"]
            time.sleep(1)

        if status == self.SAVEPOINT_COMPLETED_STATUS:
            # global save_point_path
            print("REQ2 RES - FINAL:")
            print(r.json())
            save_point_path = r.json()["operation"]["location"]
            print("Current save point is located at: ", save_point_path)

        # TODO, set parallelism per operator
        if query == "query-1":
            p1 = suggested_parallelism['Source:_BidsSource']
            p2 = suggested_parallelism['Mapper']
            p3 = suggested_parallelism['LatencySink']
            writeConfig(container=container,
                        args=["standalone-job", "--job-classname", job, "--fromSavepoint", savepoint_path, "--p-source",str(p1),
                              "--p-map",str(p2), "--p-sink",str(p3)])
        if query == "query-3":
            p1 = suggested_parallelism['Source:_auctionsSource']
            p2 = suggested_parallelism['Source:_personSource']
            p3 = suggested_parallelism['Incrementaljoin']
            writeConfig(container=container,
                        args=["standalone-job", "--job-classname", job, "--fromSavepoint", savepoint_path, "--p-auction-source",str(p1),
                              "--p-person-source",str(p2), "--p-join",str(p3)])
        if query == "query-11":
            p1 = suggested_parallelism['Source:_BidsSource']
            p2 = suggested_parallelism['SessionWindow____DummyLatencySink']
            writeConfig(container=container,
                        args=["standalone-job", "--job-classname", job, "--fromSavepoint", savepoint_path, "--p-source",str(p1),"--p-window",str(p2)])


        # autenticate with kubernetes API
        config.load_incluster_config()
        v1 = client.AppsV1Api()

        if float(previous_scaling_event) == 0 and current_number_of_taskmanagers != number_of_taskmanagers:
            print("rescaling to", number_of_taskmanagers)
            # scale taskmanager
            new_number_of_taskmanagers = number_of_taskmanagers
            body = {"spec": {"replicas": new_number_of_taskmanagers}}
            api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
        else:
            print("in cooldown")

        # delete old jobmanager
        v1 = client.BatchV1Api()
        api_response = v1.delete_namespaced_job(name="flink-jobmanager", namespace="default", pretty=True)

        time.sleep(time_after_delete_job)

        # delete the remaining jobmanager pod
        v1 = client.CoreV1Api()
        response = v1.list_namespaced_pod(namespace="default")

        # find name
        jobmanager_name = None
        for i in response.items:
            if "jobmanager" in i.metadata.name:
                print("Found jobmanager id: " + str(i.metadata.name))
                jobmanager_name = i.metadata.name

        # delete pod
        if jobmanager_name is not None:
            response = v1.delete_namespaced_pod(name=jobmanager_name, namespace="default")
            print("deleted pod")
        else:
            print("No jobmanager pod found")

        time.sleep(time_after_delete_pod)

        # deploy new job file with updated parallelism
        k8s_client = client.ApiClient()
        yaml_file = "jobmanager_from_savepoint.yaml"
        utils.create_from_yaml(k8s_client, yaml_file)