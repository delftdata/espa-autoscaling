import traceback

from common import Configurations
from .JobManagerMetricGatherer import JobManagerMetricGatherer
from .PrometheusMetricGatherer import PrometheusMetricGatherer
from .KubernetesManager import KubernetesManager

OPERATOR_TO_TOPIC_MAPPING = {
    "bidssource": "bids_topic",
    "auctionssource": "auction_topic",
    "personsource": "person_topic"
}


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
    kubernetesManager: KubernetesManager

    def __init__(self, configurations: Configurations):
        """
        Constructor of the MetricsGatherer.
        The metricsGatherer requires a Configurations class containing all necessary configurations or running the class
        :param configurations: Configurations class containing all configurations of the current run.
        """
        self.configurations = configurations
        self.jobmanagerMetricGatherer = JobManagerMetricGatherer(configurations)
        self.prometheusMetricGatherer = PrometheusMetricGatherer(configurations)
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
            currentTaskmanagers = self.kubernetesManager.getCurrentNumberOfTaskmanagersMetrics()
            if currentTaskmanagers < 0:
                print(f"Error: nokubectl  valid amount of taskmanagers found: {currentTaskmanagers}")
                return {}
            operatorParallelismInformation = {}
            for operator in knownOperators:
                operatorParallelismInformation[operator] = currentTaskmanagers
            return operatorParallelismInformation
        else:
            return self.jobmanagerMetricGatherer.getOperatorParallelism()


    def __subtractSourceNameFromOperatorName(self, operatorName: str, printError=True):
        for sourceName in OPERATOR_TO_TOPIC_MAPPING.keys():
            if sourceName in operatorName.lower():
                return sourceName
        if printError:
            print(f"Error: could not determine sourceName from operatorName '{operatorName}'")


    def getTopicFromOperatorName(self, operatorName, printError=True):
        sourceName = self.__subtractSourceNameFromOperatorName(operatorName, printError=printError)
        if sourceName in OPERATOR_TO_TOPIC_MAPPING:
            return OPERATOR_TO_TOPIC_MAPPING[sourceName]
        else:
            if printError:
                print(f"Error: could not fetch topic from operatorName '{operatorName}'")


    def gatherTopology(self, includeTopics=False):
        topology = self.jobmanagerMetricGatherer.getTopology()
        if includeTopics:
            operators = self.jobmanagerMetricGatherer.getOperators()
            for operator in operators:
                topic = self.getTopicFromOperatorName(operator, printError=False)
                if topic:
                    topology.append((topic, operator))
        return topology
