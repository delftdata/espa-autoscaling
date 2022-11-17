import traceback

from common import Configurations
from .JobManagerMetricGatherer import JobManagerMetricGatherer
from .PrometheusMetricGatherer import PrometheusMetricGatherer


class MetricsGatherer:
    """
    The MetricsGatherer class is responsible for gathering the required metrics for the autoscalers to operate.
    It contains both a MetricGatherer for fetching data from the JobManager and a MetricGather for fetching data from
    the prometheus server. In addition, it contains functionality to fetch the current parallelism of all operators in
    the current cluster.
    """

    configurations: Configurations
    jobmanagerMetricGatherer: JobManagerMetricGatherer
    prometheusMetricGatherer: PrometheusMetricGatherer
    v1 = None

    def __init__(self, configurations: Configurations):
        """
        Constructor of the MetricsGatherer.
        The metricsGatherer requires a Configurations class containing all necessary configurations or running the class
        :param configurations: Configurations class containing all configurations of the current run.
        """
        self.configurations = configurations
        self.jobmanagerMetricGatherer = JobManagerMetricGatherer(configurations)
        self.prometheusMetricGatherer = PrometheusMetricGatherer(configurations)

    def __getCurrentNumberOfTaskmanagersMetrics(self) -> int:
        """
        When using Flink reactive, the parallelism of every replica is equal to the amount of taskmanagers in the
        kubernetes cluster. This method fetches the current amount of replicas of the taskmanagers or returns -1 when
        the request fails.
        :return: Amount of taskmanagers ran in the kubernetes cluster. Returns -1 if it is unable to retrieve data from
        the server.
        """
        if self.v1:
            try:
                number_of_taskmanagers = -1
                ret = self.v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True,
                                                         field_selector="metadata.name=flink-taskmanager")
                for i in ret.items:
                    number_of_taskmanagers = int(i.spec.replicas)
                return number_of_taskmanagers
            except:
                traceback.print_exc()
                return -1
        else:
            print("Error fetching current number of taskmanagers: v1 is not defined.")

    def fetchCurrentOperatorParallelismInformation(self, knownOperators: [str] = None) -> {str, int}:
        """
        Get per-operator parallelism
        If Flink reactive is used:
            Fetch current amount of taskmanagers
            Return a direcotry with all operators having this parallelism
            v1 is required for this scenario
        If Flink reactive is not used:
            Fetch taskmanagers using the getCurrentParallelismMetrics() function.
            v1 is not required for this scenario
        :param knownOperators:
        :return: Directory with operators as key and parallelisms as values
        """
        if self.configurations.USE_FLINK_REACTIVE:
            currentTaskmanagers = self.__getCurrentNumberOfTaskmanagersMetrics()
            if currentTaskmanagers < 0:
                print(f"Error: no valid amount of taskmanagers found: {currentTaskmanagers}")
                return {}
            operatorParallelismInformation = {}
            for operator in knownOperators:
                operatorParallelismInformation[operator] = currentTaskmanagers
            return operatorParallelismInformation
        else:
            return self.jobmanagerMetricGatherer.getOperatorParallelism()
