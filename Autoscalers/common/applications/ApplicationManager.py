import traceback

from common import Configurations
from .JobmanagerManager import JobmanagerManager
from .PrometheusManager import PrometheusManager
from .KubernetesManager import KubernetesManager



class ApplicationManager:
    """
    The MetricsGatherer class is responsible for gathering the required metrics for the autoscalers to operate.
    It contains both a MetricGatherer for fetching data from the JobManager and a MetricGather for fetching data from
    the prometheus server. In addition, it contains functionality to fetch the current parallelism of all operators in
    the current cluster.
    """

    configurations: Configurations
    jobmanagerManager: JobmanagerManager
    prometheusManager: PrometheusManager
    kubernetesManager: KubernetesManager

    def __init__(self, configurations: Configurations):
        """
        Constructor of the MetricsGatherer.
        The metricsGatherer requires a Configurations class containing all necessary configurations or running the class
        :param configurations: Configurations class containing all configurations of the current run.
        """
        self.configurations = configurations
        self.jobmanagerManager = JobmanagerManager(configurations)
        self.prometheusManager = PrometheusManager(configurations)
        self.kubernetesManager = KubernetesManager(configurations)

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
            if not self.configurations.RUN_LOCALLY:
                currentTaskmanagers = self.kubernetesManager.getCurrentNumberOfTaskmanagersMetrics()
            else:
                currentTaskmanagers = max(self.prometheusManager.getAllTotalTaskslots())
            if currentTaskmanagers < 0:
                print(f"Error: no valid amount of taskmanagers found: {currentTaskmanagers}")
                return {}
            operatorParallelismInformation = {}
            for operator in knownOperators:
                operatorParallelismInformation[operator] = currentTaskmanagers
            return operatorParallelismInformation
        else:
            return self.jobmanagerManager.getOperatorParallelism()


    def gatherTopology(self, includeTopics=False):
        topology = self.jobmanagerManager.getTopology()
        if includeTopics:
            operators = self.jobmanagerManager.getOperators()
            for operator in operators:
                topic = self.configurations.experimentData.getTopicFromOperatorName(operator, printError=False)
                if topic:
                    topology.append((topic, operator))
        return topology
