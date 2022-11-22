import random
import traceback

from common import Configurations
from kubernetes import client, utils


class KubernetesManager:
    configurations: Configurations

    appsV1 = None
    batchV1 = None
    coreV1 = None


    def __init__(self, configurations: Configurations):
        self.configurations = configurations

        if not self.configurations.RUN_LOCALLY:
            self.appsV1 = client.AppsV1Api()
            self.batchV1 = client.BatchV1Api()
            self.coreV1 = client.CoreV1Api()

    # Remove current jobmanager
    def deleteJobManager(self):
        if not self.configurations.RUN_LOCALLY:
            try:
                _ = self.batchV1.delete_namespaced_job(name="flink-jobmanager", namespace="default",
                                                              pretty=True)
            except:
                print("Error: deleting jobmanager failed.")
                traceback.print_exc()
        else:
            print("Running application locally. Mocking the deletion of jobmanager")

    def deleteJobManagerPod(self):
        if not self.configurations.RUN_LOCALLY:
            try:
                # Delete jobmanager pod
                # delete the remaining jobmanager pod
                response = self.coreV1.list_namespaced_pod(namespace="default")
                # find name
                jobmanager_name = None
                for i in response.items:
                    if "jobmanager" in i.metadata.name:
                        print("Found jobmanager id: " + str(i.metadata.name))
                        jobmanager_name = i.metadata.name
                # delete pod
                if jobmanager_name is not None:
                    _ = self.coreV1.delete_namespaced_pod(name=jobmanager_name, namespace="default")
                    print("deleted pod")
                else:
                    print("No jobmanager pod found")
            except:
                print("Error: failed deleteing jobmanager pod")
                traceback.print_exc()
        else:
            print("Running application locally. Mocking the deletion of the jobmanager pod")

    # Set amount of Flink Taskmanagers
    def adaptFlinkTaskmanagersParallelism(self, new_number_of_taskmanagers):
        if not self.configurations.RUN_LOCALLY:
            try:
                print(f"Scaling total amount of taskmanagers to {new_number_of_taskmanagers}")
                body = {"spec": {"replicas": new_number_of_taskmanagers}}
                _ = self.appsV1.patch_namespaced_deployment_scale(
                    name="flink-taskmanager", namespace="default", body=body,
                    pretty=True)
            except:
                traceback.print_exc()
        print(f"Running application locally. Mocking the adaption of taskmanagers to '{new_number_of_taskmanagers}' "
              f"taskmanagers")


    def getCurrentNumberOfTaskmanagersMetrics(self) -> int:
        """
        When using Flink reactive, the parallelism of every replica is equal to the amount of taskmanagers in the
        kubernetes cluster. This method fetches the current amount of replicas of the taskmanagers or returns -1 when
        the request fails.
        :return: Amount of taskmanagers ran in the kubernetes cluster. Returns -1 if it is unable to retrieve data from
        the server.
        """
        if not self.configurations.RUN_LOCALLY:
            try:
                number_of_taskmanagers = -1
                ret = self.appsV1.list_namespaced_deployment(watch=False, namespace="default", pretty=True,
                                                         field_selector="metadata.name=flink-taskmanager")
                for i in ret.items:
                    number_of_taskmanagers = int(i.spec.replicas)
                return number_of_taskmanagers
            except:
                traceback.print_exc()
                return -1
        else:
            randomAmountOfTaskmanagers = random.randint(self.configurations.MIN_PARALLELISM,
                                                        self.configurations.MAX_PARALLELISM)
            print(f"Running application locally. Returning random amount of: {randomAmountOfTaskmanagers} taskmanagers,"
                  f"selected between [{self.configurations.MIN_PARALLELISM}, {self.configurations.MAX_PARALLELISM}].")
            return randomAmountOfTaskmanagers

    def deployNewJobManager(self, yaml_file: str):
        if not self.configurations.RUN_LOCALLY:
            utils.create_from_yaml(self.appsV1, yaml_file)
        else:
            print(f"Deploying new jobmanager form file '{yaml_file}. Mocking execution.")
