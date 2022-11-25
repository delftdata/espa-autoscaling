import random
import traceback

from common import Configurations
from kubernetes import client, utils, config


class KubernetesManager:
    configurations: Configurations

    appsV1 = None
    batchV1 = None
    coreV1 = None
    k8s_client = None


    def __init__(self, configurations: Configurations):
        self.configurations = configurations

        if not self.configurations.RUN_LOCALLY:
            config.load_incluster_config()
            self.appsV1 = client.AppsV1Api()
            self.batchV1 = client.BatchV1Api()
            self.coreV1 = client.CoreV1Api()
            self.k8s_client = client.ApiClient()

    @staticmethod
    def __mockKubernetesInteraction(operation: str, command: str):
        print(f"Executing the following operation locally: {operation}")
        print(f"Please execute the following command. Then press any key to continue...")
        print(f"\t{command}")
        input()
        print("")

    # Remove current jobmanager
    def deleteJobManager(self):
        if not self.configurations.RUN_LOCALLY:
            try:
                _ = self.batchV1.delete_namespaced_job(name="flink-jobmanager", pretty=True,
                                                       namespace=self.configurations.KUBERNETES_NAMESPACE)
            except:
                print("Error: deleting jobmanager failed.")
                traceback.print_exc()
        else:
            self.__mockKubernetesInteraction(
                operation="Deleting jobmanager job",
                command=f"kubectl delete job flink-jobmanager"
            )

    def deleteJobManagerPod(self):
        if not self.configurations.RUN_LOCALLY:
            try:
                # Delete jobmanager pod
                # delete the remaining jobmanager pod
                response = self.coreV1.list_namespaced_pod(namespace=self.configurations.KUBERNETES_NAMESPACE)
                # find name
                jobmanager_name = None
                for i in response.items:
                    if "jobmanager" in i.metadata.name:
                        print("Found jobmanager id: " + str(i.metadata.name))
                        jobmanager_name = i.metadata.name
                # delete pod
                if jobmanager_name is not None:
                    _ = self.coreV1.delete_namespaced_pod(name=jobmanager_name,
                                                          namespace=self.configurations.KUBERNETES_NAMESPACE)
                    print("deleted pod")
                else:
                    print("No jobmanager pod found")
            except:
                print("Error: failed deleting jobmanager pod")
                traceback.print_exc()
        else:
            self.__mockKubernetesInteraction(
                operation="Delete jobmanager pod",
                command=f"kubectl delete pods "
                        "$(kubectl get pods -o yaml | grep flink-jobmanager- | grep name | awk '{print $2}')"
            )

    # Set amount of Flink Taskmanagers
    def adaptFlinkTaskmanagersParallelism(self, new_number_of_taskmanagers):
        f"""
        Change the parallelism of the online taskmanagers to new_number_of_taskmanagers.
        This is done by sending a request to self.appsV1.patched_namespaced_deployment_scale.
        If an error occurs, an error is thrown and the program continues as normal.
        If self.configuratinos.RUN_LOCALLY is true, nothing is done.
        :param new_number_of_taskmanagers: 
        :return: None
        """
        if not self.configurations.RUN_LOCALLY:
            try:
                print(f"Scaling total amount of taskmanagers to {new_number_of_taskmanagers}")
                body = {"spec": {"replicas": new_number_of_taskmanagers}}
                _ = self.appsV1.patch_namespaced_deployment_scale(
                    name="flink-taskmanager", namespace=self.configurations.KUBERNETES_NAMESPACE, body=body,
                    pretty=True)
            except:
                traceback.print_exc()
        else:
            self.__mockKubernetesInteraction(
                operation=f"Adapting parallelism of taskmanagers to {new_number_of_taskmanagers}",
                command=f"kubectl scale deploy flink-taskmanager --replicas={new_number_of_taskmanagers}"
            )


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
                ret = self.appsV1.list_namespaced_deployment(watch=False, pretty=True,
                                                             namespace=self.configurations.KUBERNETES_NAMESPACE,
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

            utils.create_from_yaml(self.k8s_client, yaml_file)
        else:
            self.__mockKubernetesInteraction(
                operation=f"Deploying a new jobmanager from file {yaml_file}",
                command=f"kubectl apply -f {yaml_file}"
            )

