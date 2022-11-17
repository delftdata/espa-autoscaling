import traceback

from common import Configurations
from .JobManagerMetricGatherer import JobManagerMetricGatherer
from .PrometheusMetricGatherer import PrometheusMetricGatherer


class MetricsGatherer:
    configurations: Configurations
    jobmanagerMetricGatherer: JobManagerMetricGatherer
    prometheusMetricGatherer: PrometheusMetricGatherer
    v1 = None

    def __init__(self, configurations: Configurations):
        self.configurations = configurations
        self.jobmanagerMetricGatherer = JobManagerMetricGatherer(configurations)
        self.prometheusMetricGatherer = PrometheusMetricGatherer(configurations)

    def __getCurrentNumberOfTaskmanagersMetrics(self) -> int:
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
