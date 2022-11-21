import requests

from common import Configurations


class PrometheusMetricGatherer:
    """
    The PrometheusMetricGatherer is responsible for fetching data from the Prometheus server.
    """

    configurations: Configurations

    def __init__(self, configurations: Configurations):
        """
        The constructor of the PrometheusMetricsGather. It requires a Configurations class containing necessary
        information about the Prometheus server.
        :param configurations: Configurations class containing the location of the Prometheus server
        """
        self.configurations = configurations

    # Prometheus fetching
    def __getResultsFromPrometheus(self, query):
        """
        Get the results of a query from Prometheus.
        Prometheus should be fetched from PROMETHEUS_SERVER
        :param query: Query to fetch results for from Prometheus
        :return: A response object send by the Prometheus server.
        """
        url = f"http://{self.configurations.PROMETHEUS_SERVER}/api/v1/query?query={query}"
        return requests.get(url)

    ############################################
    # Operator-based subtraction
    @staticmethod
    def __extract_per_operator_metrics(prometheusResponse):
        """
        Extract per-operator- metrics from the prometheusResponse
        :param prometheusResponse: Response received from Prometheus containing query results
        :return: A directory with per-operator values {operator: values}
        """
        metrics = prometheusResponse.json()["data"]["result"]
        metrics_per_operator = {}
        for operator in metrics:
            metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
        return metrics_per_operator


    def getOperatorIdleTimePerSecond(self) -> {str, float}:
        """
        Get idle time per second operators spend idle per task
        :return: {operator:str -> idleTime per second: float}
        """
        idleTimeMsPerSecond_query = f"avg(avg_over_time(flink_taskmanager_job_task_idleTimeMsPerSecond" \
                                    f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])/1000) by (task_name)"
        idleTimeMsPerSecond_data = self.__getResultsFromPrometheus(idleTimeMsPerSecond_query)
        idleTimeMsPerSecond = self.__extract_per_operator_metrics(idleTimeMsPerSecond_data)
        return idleTimeMsPerSecond

    # Buffer In usage
    def getOperatorSumBufferInUsageMetrics(self) -> {str, float}:
        inputBufferUsageSum_query = f"sum(avg_over_time(flink_taskmanager_job_task_buffers_inPoolUsage" \
                                    f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        inputBufferUsageSum_data = self.__getResultsFromPrometheus(inputBufferUsageSum_query)
        inputBufferUsageSum = self.__extract_per_operator_metrics(inputBufferUsageSum_data)
        return inputBufferUsageSum

    def getOperatorMaximumBuffersInUsageMetrics(self) -> {str, float}:
        """
        Fetch maximum inputBuffer usage of every operator
        :return: A directory with the maximum input buffer usage of every operator.
        """
        input_usage_maximum_query = f"max(avg_over_time(flink_taskmanager_job_task_buffers_inPoolUsage" \
                                    f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        input_usage_maximum_data = self.__getResultsFromPrometheus(input_usage_maximum_query)
        input_usage_maximum = self.__extract_per_operator_metrics(input_usage_maximum_data)
        return input_usage_maximum

    # Parallelism gathering
    def getOperatorCurrentParallelismMetrics(self) -> {str, int}:
        """
        Get the current parallelisms of the individual operators
        :return: A directory with {operator, currentParallelism}
        """
        parallelism_query = f"count(sum_over_time(flink_taskmanager_job_task_operator_numRecordsIn" \
                            f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        parallelism_data = self.__getResultsFromPrometheus(parallelism_query)
        parallelism = self.__extract_per_operator_metrics(parallelism_data)
        return parallelism

    # Get operators Backpressure time per second
    def getOperatorBackpressureTimeMetrics(self, monitoringPeriodSeconds=None) -> {str, float}:
        """
        Get backpressure time of all operators.
        If monitoring_period_seconds is provided, this will be used as a period to gather metrics for.
        Else self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS is used.
        :param monitoringPeriodSeconds: Optional parameter to determine aggregation period.
        :return:
        """
        gatherPeriod = monitoringPeriodSeconds if monitoringPeriodSeconds else self.configurations.\
            METRIC_AGGREGATION_PERIOD_SECONDS
        backpressure_time_query = f"avg(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond" \
                                  f"[{gatherPeriod}s]) / 1000) by (task_name)"
        backpressure_time_data = self.__getResultsFromPrometheus(backpressure_time_query)
        backpressure_time = self.__extract_per_operator_metrics(backpressure_time_data)
        return backpressure_time

    def getOperatorBackpressureStatusMetrics(self) -> {str, bool}:
        """
        Get backpressure status of all operators from prometheus.
        :return: A direcotry of {operator, boolean} with the boolean indicating whether the operator is backpressured
        """
        backpressure_query = f"max_over_time(flink_taskmanager_job_task_isBackPressured" \
                             f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        backpressure_data = self.__getResultsFromPrometheus(backpressure_query)
        backpressure = self.__extract_per_operator_metrics(backpressure_data)
        results = {}
        for k, v in backpressure.items():
            results[k] = v == 1.0
        return results


    def getOperatorKafkaLag(self) -> {str, int}:
        kafkaLag_query = "sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * "\
                         "flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions) " \
                         "by (task_name)"
        kafkaLag_data = self.__getResultsFromPrometheus(kafkaLag_query)
        kafkaLag = self.__extract_per_operator_metrics(kafkaLag_data)
        return kafkaLag

    ############################################
    # Taskmanager based substraction
    @staticmethod
    def __extract_per_taskmanager_metrics(prometheusResponse):
        """
        Given a prometheus response, extract the metris per operator.
        As key use the tm_id and as value the value provided by prometheus.
        :param prometheusResponse: A Get response from the prometheus server.
        :return: A directory with as key the taskmanagers tm_id and as value to provided metric {tm_id -> value}
        """
        metrics = prometheusResponse.json()["data"]["result"]
        metrics_per_operator = {}
        for operator in metrics:
            taskmanager_id = operator["metric"]["tm_id"]
            metrics_per_operator[taskmanager_id] = float(operator["value"][1])
        return metrics_per_operator

    def getTaskmanagerJVMCPUUSAGE(self) -> {str, int}:
        """
        Get the CPU usage of every taskmanager
        :return:
        """
        TaskmanagerJVM_CPUUsage_query = f"avg_over_time(flink_taskmanager_Status_JVM_CPU_Load" \
                                        f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        TaskmanagerJVM_CPUUsage_data = self.__getResultsFromPrometheus(TaskmanagerJVM_CPUUsage_query)
        TaskmanagerJVM_CPUUsage = self.__extract_per_taskmanager_metrics(TaskmanagerJVM_CPUUsage_data)
        return TaskmanagerJVM_CPUUsage

    ############################################
    # Kafka topic subtraction
    @staticmethod
    def __extract_per_topic_metrics(prometheusResponse):
        """
        Given a prometheus response, extract the metrics per topic.
        As key use the topic and as value the value provided by prometheus.
        :param prometheusResponse: A Get response from the prometheus server.
        :return: A directory with as key the taskmanagers tm_id and as value to provided metric {topic -> value}
        :param prometheusResponse:
        :return:
        """
        metrics = prometheusResponse.json()["data"]["result"]
        metrics_per_operator = {}
        for operator in metrics:
            topic = operator["metric"]["topic"]
            metrics_per_operator[topic] = float(operator["value"][1])
        return metrics_per_operator

    def getTopicKafkaInputRates(self) -> {str, int}:
        """
        Takes the average input rate per second and aggregates it as sum per topic.

        :return:
        """
        kafkaInputRate_query = f"sum(rate(kafka_server_brokertopicmetrics_messagesin_total" \
                               f"\u007btopic!='',topic!='__consumer_offsets'\u007d" \
                               f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (topic)"
        kafkaInputRate_data = self.__getResultsFromPrometheus(kafkaInputRate_query)
        kafkaInputRate = self.__extract_per_topic_metrics(kafkaInputRate_data)
        return kafkaInputRate


    #######################################################
    # Subtask subtraction
    @staticmethod
    def __extract_per_subtask_metrics(prometheusResponse):
        """
        Extract per-subtask metrics.
        subtaskname: "{operator_name} {subtask_index}"
        :param prometheusResponse: Response from prometheus to get information from
        :return: Directory with {"{task_name subtask_index}": str -> value}
        """
        metrics = prometheusResponse.json()["data"]["result"]
        metrics_per_subtask = {}
        for subtask in metrics:
            task_name = subtask["metric"]["task_name"]
            subtask_id = subtask["metric"]["subtask_index"]
            subtaskName = f"{task_name} {subtask_id}"
            metrics_per_subtask[subtaskName] = float(subtask["value"][1])
        return metrics_per_subtask

    def getSubtaskInputRateMetrics(self) -> {str, float}:
        # originally it used the rate(numRecordsIn)
        subtask_inputRate_query = f"rate(flink_taskmanager_job_task_operator_numRecordsIn" \
                          f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        subtask_inputRate_data = self.__getResultsFromPrometheus(subtask_inputRate_query)
        subtask_inputRate = self.__extract_per_subtask_metrics(subtask_inputRate_data)
        return subtask_inputRate

    def getSubtaskOutputRateMetrics(self) -> {str, float}:
        subtask_outputRate_query = f"avg_over_time(flink_taskmanager_job_task_numRecordsOutPerSecond" \
                           f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        subtask_outputRate_data = self.__getResultsFromPrometheus(subtask_outputRate_query)
        subtask_outputRates = self.__extract_per_subtask_metrics(subtask_outputRate_data)
        return subtask_outputRates

    def getSubtaskBusyTimeMetrics(self) -> {str, float}:
        subtask_busyTime_query = f"avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond" \
                         f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])/1000"
        subtask_busyTime_data = self.__getResultsFromPrometheus(subtask_busyTime_query)
        subtask_busyTime = self.__extract_per_subtask_metrics(subtask_busyTime_data)
        return subtask_busyTime
