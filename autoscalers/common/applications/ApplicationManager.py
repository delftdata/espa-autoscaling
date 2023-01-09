from common import Configurations
from typing import Any
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

    def initialize(self):
        self.kubernetesManager.initialize()


    def fetch_current_operator_parallelism_information(self, known_operators: [str] = None) -> {str, int}:
        """
        Get per-operator parallelism
        If Flink reactive is used:
            Fetch current amount of taskmanagers
            Return a directory with all operators having this parallelism
            v1 is required for this scenario
        If Flink reactive is not used:
            Fetch taskmanagers using the getCurrentParallelismMetrics() function.
            v1 is not required for this scenario
        :param known_operators:
        :return: Directory with operators as key and parallelisms as values
        """
        if self.configurations.USE_FLINK_REACTIVE:
            if not self.configurations.RUN_LOCALLY:
                current_taskmanagers = self.kubernetesManager.get_current_number_of_taskmanagers_metrics()
            else:
                current_taskmanagers = max(self.prometheusManager.get_all_total_taskslots())
            if current_taskmanagers < 0:
                print(f"Error: no valid amount of taskmanagers found: {current_taskmanagers}")
                return {}
            operator_Parallelism_information = {}
            for operator in known_operators:
                operator_Parallelism_information[operator] = current_taskmanagers
            return operator_Parallelism_information
        else:
            return self.jobmanagerManager.getOperatorParallelism()


    def gather_topology(self, include_topics=False) -> [(str, str)]:
        """
        Get a list representing the topology of the current job. The provided topology consists out of a list of edges,
        with each edge represented as a 2-way tuple: (l_operator, r_operator), indicating a directed edge as
        l_operator -> r_operator
        :param: include_topics: Whether to also include topics in the topology. These are added as an additional edge
        from the topic to the source.
        :return: List of directed edges represented as a 2-way tuple.
        """
        topology = self.jobmanagerManager.getTopology()
        if include_topics:
            operators = self.jobmanagerManager.getOperators()
            for operator in operators:
                topic = self.configurations.experimentData.get_topic_from_operator_name(operator, print_error=False)
                if topic:
                    topology.append((topic, operator))
        return topology


    def gather_bottleneck_operators(self, topology: [(str, str)], kafka_source_is_backpressured_threshold=1000,
                                    operator_backpressure_status_metrics: dict[str, bool] = None,
                                    source_operator_backpressure_status_metrics: dict[str, bool] = None,
                                    print_metrics=False):
        """
        Get all operators that are causing backpressure in the system.
        An operator is said to cause backpressure if it is not experiencing backpressure itself, but at least one of its
        upstream operators is.
        :param: topology: The topology of the system, containing directed edges (lop -> rop)
        :param: kafka_source_is_backpressured_threshold: Threshold for determining whether sources are backpressured. The
        threshold is set to 1000 by default. This threshold is only used of no sourceOperatorBackpressureStatusMetrics
        are provided.
        :param: operator_backpressure_status_metrics: Metrics indicating whether operators are experiencing backpressure.
        When not provided, they are fetched from prometheus.
        :param: source_operator_backpressure_status_metrics: Metrics indicating whether operators are causing backpressure in
        the kafka sources. When not provided, they are fetched from prometheus using param
        kafka_source_is_backpressured_threshold as threshold.
        :param: print_metrics Whether to print the metrics to console.
        :return: A list of operators causing backpressure.
        """
        if not operator_backpressure_status_metrics:
            operator_backpressure_status_metrics = self.prometheusManager.get_operator_backpressure_status_metrics()
        if not source_operator_backpressure_status_metrics:
            source_operator_backpressure_status_metrics = self.prometheusManager.get_source_operator_backpressure_status_metrics(
                    kafka_source_is_backpressured_threshold)

        if print_metrics:
            print(f"Source-operator's backpressure status: '{source_operator_backpressure_status_metrics}'")
            print(f"Operator's backpressure status: '{operator_backpressure_status_metrics}'")
            print(f"Topology: '{topology}")

        bottleneck_operator_set: set = set()
        for l_operator, r_operator in topology:
            if l_operator not in operator_backpressure_status_metrics:
                print(f"Error: right operator '{r_operator}' of topology '{topology}' not found in backpressure status "
                      f"metrics '{operator_backpressure_status_metrics}'.")
                continue
            if r_operator not in operator_backpressure_status_metrics:
                print(
                    f"Error: right operator '{r_operator}' of topology '{topology}' not found in backpressure status "
                    f"metrics '{operator_backpressure_status_metrics}'.")
                continue

            # if lOperator is experiencing backpressure
            if operator_backpressure_status_metrics[l_operator]:
                # if its downstream operator is not experiencing backpressure
                if not operator_backpressure_status_metrics[r_operator]:
                    # its downstream operator is the cause of the backpressure
                    bottleneck_operator_set.add(r_operator)
            # if lOperator is not experiencing backpressure
            else:
                # if lOperator is a source
                if l_operator in source_operator_backpressure_status_metrics:
                    # if the kafka source corresponding to lOperator is being backpressured
                    if source_operator_backpressure_status_metrics[l_operator]:
                        # the source lOperator is causing backpressure
                        bottleneck_operator_set.add(l_operator)

        return list(bottleneck_operator_set)

    @staticmethod
    def operator_in_dictionary(operator: str, dictionary: dict[str, Any], dictionary_name: str = "") -> bool:
        """
        Helper function that checks whether an operator is in the provided dictionary. If it is not in the dictionary, it returns false and
        prints to console.
        :param operator: Operator that should be a key in the provided dictionary
        :param dictionary: Dictionary to check whether the operator is in.
        :param dictionary_name:
        :return: Boolean indicating whether operator is in dictionary
        """
        if operator in dictionary:
            return True
        else:
            dictionary_name = f" {dictionary_name}" if dictionary_name else ""
            print(f"Error: operator '{operator}' is not in {dictionary_name}'{dictionary}'.")
            return False

# Debugging purposes
    def print_metrics(self, metric_name_data_dict: dict[str, Any]):
        """
        Print a dictionary with (metric_name: metrics).
        :param metric_name_data_dict: As key we have the metric's name and as value the dictionary containing the metrics
        :return: None
        """
        print("Found te following metrics:")
        for metric_name, metric_data in metric_name_data_dict.items():
            self.print_metric(metric_name, metric_data)

    @staticmethod
    def print_metric(metric_name: str, data_dict):
        """
        Print the provided metric_name and data_dict to console.
        :param metric_name: Name of the metric to print.
        :param data_dict: Data to print
        :return: None
        """
        metric_name = metric_name.capitalize()
        print(f"{metric_name}: '{data_dict}'")
