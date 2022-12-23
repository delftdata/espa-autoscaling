import random
import traceback
import time

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

    def initialize(self):
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
                print("Deleted jobmanager job")
            except:
                print("Error: deleting jobmanager failed.")
                traceback.print_exc()
        else:
            self.__mockKubernetesInteraction(
                operation="Deleting jobmanager job",
                command=f"kubectl delete job flink-jobmanager"
            )

    def waitUntilAllJobmanagerJobsAreRemoved(self):
        """
        Wait until no pod containing the name 'jobmanager' is online anymore.
        If a list_namespaced_pod request fails, the method is returned.
        """
        jobmanager_jobs_is_online = True
        while jobmanager_jobs_is_online:
            print("Waiting until jobmanager job is removed.")
            jobmanager_jobs_is_online = False
            time.sleep(1)
            try:
                response = self.batchV1.list_namespaced_job(namespace=self.configurations.KUBERNETES_NAMESPACE)
                # check whether a pod named jobmanager is still online
                for i in response.items:
                    if "jobmanager" in i.metadata.name:
                        jobmanager_jobs_is_online = True
            except:
                print("Error: failed fetching information about jobs in namespace")
                traceback.print_exc()
        print("Jobmanager job is removed.")

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
                        jobmanager_name = i.metadata.name
                        print(f"Found jobmanager pod id: {jobmanager_name}")

                # delete pod
                if jobmanager_name is not None:
                    _ = self.coreV1.delete_namespaced_pod(name=jobmanager_name,
                                                          namespace=self.configurations.KUBERNETES_NAMESPACE)
                    print(f"Deleted pod {jobmanager_name}")
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

    def waitUntilAllJobmanagerPodsAreRemoved(self):
        """
        Wait until no pod containing the name 'jobmanager' is online anymore.
        If a list_namespaced_pod request fails, the method is returned.
        """
        jobmanager_pods_is_online = True
        while jobmanager_pods_is_online:
            print("Waiting until jobmanager pod is removed.")
            jobmanager_pods_is_online = False
            time.sleep(1)
            try:
                response = self.coreV1.list_namespaced_pod(namespace=self.configurations.KUBERNETES_NAMESPACE)
                # check whether a pod named jobmanager is still online
                for i in response.items:
                    if "jobmanager" in i.metadata.name:
                        jobmanager_pods_is_online = True
            except:
                print("Error: failed fetching information about pods in namespace")
                traceback.print_exc()
        print("Jobmanager pod is removed.")

    def deleteJobManagerService(self):
        if not self.configurations.RUN_LOCALLY:
            try:
                # Delete jobmanager service
                # delete the remaining jobmanager service
                response = self.coreV1.list_namespaced_service(namespace=self.configurations.KUBERNETES_NAMESPACE)
                # find name
                jobmanager_service_name = None
                for i in response.items:
                    if "jobmanager" in i.metadata.name:
                        jobmanager_service_name = i.metadata.name
                        print(f"Found jobmanager service id: {jobmanager_service_name}")

                # delete service
                if jobmanager_service_name is not None:
                    _ = self.coreV1.delete_namespaced_service(name=jobmanager_service_name,
                                                              namespace=self.configurations.KUBERNETES_NAMESPACE)
                    print(f"Deleted service {jobmanager_service_name}")
                else:
                    print("No jobmanager service found")
            except:
                print("Error: failed deleting jobmanager service")
                traceback.print_exc()
        else:
            self.__mockKubernetesInteraction(
                operation="Delete jobmanager service",
                command=f"kubectl delete service "
                        "$(kubectl get pods -o yaml | grep flink-jobmanager- | grep name | awk '{print $2}')"
            )

    def waitUntilAllJobmanagerServicesAreRemoved(self):
        """
        Wait until no service containing the name 'jobmanager' is online anymore.
        If a list_namespaced_pod request fails, the method is returned.
        """
        jobmanager_service_is_online = True
        while jobmanager_service_is_online:
            print("Waiting until jobmanager service is removed.")
            jobmanager_service_is_online = False
            time.sleep(1)
            try:
                response = self.coreV1.list_namespaced_service(namespace=self.configurations.KUBERNETES_NAMESPACE)
                # check whether a service named jobmanager is still online
                for i in response.items:
                    if "jobmanager" in i.metadata.name:
                        jobmanager_service_is_online = True
            except:
                print("Error: failed fetching information about services in namespace")
                traceback.print_exc()
        print("Jobmanager service is removed.")

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

    def waitUntilAllTaskmanagersAreRunning(self):
        """
        Wait until no pod containing the name 'flink-taskmanager' are running.
        If a list_namespaced_pod request fails, the method is returned.
        """
        not_running_taskmanagers: [str] = ["Initializing"]
        while not_running_taskmanagers:
            not_running_taskmanagers = []
            try:
                response = self.coreV1.list_namespaced_pod(namespace=self.configurations.KUBERNETES_NAMESPACE)
                for i in response.items:
                    name = i.metadata.name
                    if "flink-taskmanager" in name:
                        phase = i.status.phase
                        if phase != "Running":
                            not_running_taskmanagers.append(name)
                if not_running_taskmanagers:
                    print(f"Waiting for the following taskmanagers to start running: {not_running_taskmanagers}")
            except:
                print("Error: failed fetching information about pods in namespace")
                traceback.print_exc()
            time.sleep(1)
        print("All taskmanager pods are running.")


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
            randomAmountOfTaskmanagers = random.randint(1, self.configurations.AVAILABLE_TASKMANAGERS)
            print(f"Running application locally. Returning random amount of: {randomAmountOfTaskmanagers} taskmanagers,"
                  f"selected between [1, {self.configurations.AVAILABLE_TASKMANAGERS}].")
            return randomAmountOfTaskmanagers

    def deployNewJobManager(self, yaml_file: str):
        if not self.configurations.RUN_LOCALLY:
            print(f"Deploying new jobmanager from file {yaml_file}")
            utils.create_from_yaml(self.k8s_client, yaml_file, namespace=self.configurations.KUBERNETES_NAMESPACE)
        else:
            self.__mockKubernetesInteraction(
                operation=f"Deploying a new jobmanager from file {yaml_file}",
                command=f"kubectl apply -f {yaml_file}"
            )
