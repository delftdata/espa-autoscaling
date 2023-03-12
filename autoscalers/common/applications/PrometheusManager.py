from typing import Any

import requests

from common import Configurations


class PrometheusManager:
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
    def __get_results_from_prometheus(self, query) -> Any:
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
    def __extract_per_operator_metrics(prometheusResponse) -> dict[str, Any]:
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


    def get_operator_idle_time_per_second(self) -> dict[str, float]:
        """
        Get idle time per second operators spend idle per task
        :return: {operator:str -> idleTime per second: float}
        """
        idle_time_ms_per_second_query = f"avg(avg_over_time(flink_taskmanager_job_task_idleTimeMsPerSecond" \
                                        f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])/1000) by (task_name)"
        idle_time_ms_per_second_data = self.__get_results_from_prometheus(idle_time_ms_per_second_query)
        idle_time_ms_per_second = self.__extract_per_operator_metrics(idle_time_ms_per_second_data)
        return idle_time_ms_per_second

    # Buffer In usage
    def get_operator_average_buffer_in_usage_metrics(self) -> dict[str, float]:
        """
        Get the average of bufferin-usage of every operator from prometheus
        """
        input_buffer_usage_sum_query = f"avg(avg_over_time(flink_taskmanager_job_task_buffers_inPoolUsage" \
                                       f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        input_buffer_usage_sum_data = self.__get_results_from_prometheus(input_buffer_usage_sum_query)
        input_buffer_usage_sum = self.__extract_per_operator_metrics(input_buffer_usage_sum_data)
        return input_buffer_usage_sum

    # Get operators Backpressure time per second
    def get_operator_backpressure_time_metrics(self, monitoringPeriodSeconds=None) -> dict[str, float]:
        """
        Get backpressure time of all operators.
        If monitoring_period_seconds is provided, this will be used as a period to gather metrics for.
        Else self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS is used.
        :param monitoringPeriodSeconds: Optional parameter to determine aggregation period.
        :return:
        """
        gather_period = monitoringPeriodSeconds if monitoringPeriodSeconds else self.configurations.\
            METRIC_AGGREGATION_PERIOD_SECONDS
        backpressure_time_query = f"avg(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond" \
                                  f"[{gather_period}s]) / 1000) by (task_name)"
        backpressure_time_data = self.__get_results_from_prometheus(backpressure_time_query)
        backpressure_time = self.__extract_per_operator_metrics(backpressure_time_data)
        return backpressure_time

    def get_operator_backpressure_status_metrics(self) -> dict[str, bool]:
        """
        Get backpressure status of all operators from prometheus.
        :return: A direcotry of {operator, boolean} with the boolean indicating whether the operator is backpressured
        """
        backpressure_query = f"max_over_time(flink_taskmanager_job_task_isBackPressured" \
                             f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        backpressure_data = self.__get_results_from_prometheus(backpressure_query)
        backpressure = self.__extract_per_operator_metrics(backpressure_data)
        results = {}
        for k, v in backpressure.items():
            results[k] = v == 1.0
        return results

    def get_operator_kafka_lag(self) -> dict[str, int]:
        """
        Get the total number of kafka lag from prometheus. This is done by fetching the total amount of pending records
        per source operator.
        """
        return self.get_source_operator_pending_records()

    def get_operator_kafka_deriv_lag(self) -> dict[str, int]:
        """
        Get the total number of kafka lag from prometheus. This is done by fetching the total amount of pending records
        per source operator.
        """
        return self.get_source_operator_pending_records()

    def get_source_operator_pending_records(self) -> dict[str, int]:
        """
        Get the total number of kafka lag from prometheus. This is fetched by summing the total number of pending
        records per task_name
        """
        kafka_lag_query = f"sum(avg_over_time(flink_taskmanager_job_task_operator_pendingRecords" \
                         f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        kafka_lag_data = self.__get_results_from_prometheus(kafka_lag_query)
        kafka_lag = self.__extract_per_operator_metrics(kafka_lag_data)
        return kafka_lag

    def get_source_operator_pending_records_derivative(self, derivative_period_seconds: int = None) -> dict[str, float]:
        """
        Get the derivative of of kafka lag from prometheus. This is fetched by summing the total number of pending
        records per task_name and is estimated using the provided {derivativeAggregationPeriod}. If
        the derivativeAggregationPeriod is not provided, self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS is used.
        """
        if not derivative_period_seconds:
            derivative_period_seconds = self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS
        kafkaLagDerivative_query = f"deriv(sum(flink_taskmanager_job_task_operator_pendingRecords) by (task_name)" \
                                   f"[{derivative_period_seconds}s:1s])"
        kafka_lag_derivative_data = self.__get_results_from_prometheus(kafkaLagDerivative_query)
        kafka_lag_derivative = self.__extract_per_operator_metrics(kafka_lag_derivative_data)
        return kafka_lag_derivative

    def get_source_operator_pending_records_rate(self) -> {str, float}:
        """
        Get the rate of the pending records of the source operators
        """
        source_pending_records_rate_query = \
            f"sum(rate(flink_taskmanager_job_task_operator_pendingRecords" \
            f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        source_pending_records_rate_data = self.__get_results_from_prometheus(source_pending_records_rate_query)
        source_pending_records_rate = self.__extract_per_operator_metrics(source_pending_records_rate_data)
        return source_pending_records_rate

    def get_source_operator_consumed_records_rate(self) -> {str, float}:
        """
        Get the rate of the consumed records of the source operators
        """
        source_pending_records_rate_query = \
            f"sum(rate(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_consumed_total" \
            f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        source_pending_records_rate_data = self.__get_results_from_prometheus(source_pending_records_rate_query)
        source_pending_records_rate = self.__extract_per_operator_metrics(source_pending_records_rate_data)
        return source_pending_records_rate

    def get_source_operator_backpressure_status_metrics(self, kafka_source_is_backpressured_threshold: int) -> {str, bool}:
        """
        Get a list of source operators, whose upstream kafka source is experiencing backpressure.
        An upstream kafka source is experiencing backpressure if its pendingRecordsRate is positive
        """
        source_operator_pending_records_rate_metrics = self.get_source_operator_pending_records_rate()

        source_backpressure_status_metrics: dict[str, bool] = {}
        for source, pendingRecordsRate in source_operator_pending_records_rate_metrics.items():
            # source is backpressured if pendingRecordsRate is larger than threshold
            source_backpressure_status_metrics[source] = pendingRecordsRate > kafka_source_is_backpressured_threshold
        return source_backpressure_status_metrics

    ############################################
    # Taskmanager based substraction
    @staticmethod
    def __extract_per_taskmanager_metrics(prometheus_response) -> dict[str, Any]:
        """
        Given a prometheus response, extract the metris per operator.
        As key use the tm_id and as value the value provided by prometheus.
        :param prometheus_response: A Get response from the prometheus server.
        :return: A directory with as key the taskmanagers tm_id and as value to provided metric {tm_id -> value}
        """
        metrics = prometheus_response.json()["data"]["result"]
        metrics_per_operator = {}
        for operator in metrics:
            taskmanager_id = operator["metric"]["tm_id"]
            metrics_per_operator[taskmanager_id] = float(operator["value"][1])
        return metrics_per_operator

    def get_taskmanager_jvm_cpu_usage(self) -> dict[str, float]:
        """
        Get the CPU usage of every taskmanager
        :return:
        """
        taskmanager_jvm_cpu_usage_query = f"avg_over_time(flink_taskmanager_Status_JVM_CPU_Load" \
                                        f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        taskmanager_jvm_cpu_usage_data = self.__get_results_from_prometheus(taskmanager_jvm_cpu_usage_query)
        taskmanager_jvm_cpu_usage = self.__extract_per_taskmanager_metrics(taskmanager_jvm_cpu_usage_data)
        return taskmanager_jvm_cpu_usage

    ############################################
    # Kafka topic subtraction
    @staticmethod
    def __extract_per_topic_metrics(prometheusResponse) -> dict[str, Any]:
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

    def get_topic_kafka_input_rates(self) -> dict[str, int]:
        """
        Takes the average input rate per second and aggregates it as sum per topic.
        :return: Dictioanry with kafka topic as str and input rates as integer.
        """
        kafka_input_rate_query = f"sum(rate(kafka_server_brokertopicmetrics_messagesin_total" \
                               f"\u007btopic!='',topic!='__consumer_offsets'\u007d" \
                               f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (topic)"
        kafka_input_rate_data = self.__get_results_from_prometheus(kafka_input_rate_query)
        kafka_input_rate = self.__extract_per_topic_metrics(kafka_input_rate_data)
        return kafka_input_rate

    #######################################################
    # Subtask subtraction
    @staticmethod
    def __extract_per_subtask_metrics(prometheusResponse) -> dict[str, Any]:
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
            subtask_name = f"{task_name} {subtask_id}"
            metrics_per_subtask[subtask_name] = float(subtask["value"][1])
        return metrics_per_subtask

    def get_subtask_input_rate_metrics(self) -> dict[str, int]:
        """
        Get input rates of all subtasks
        :return: Dictionary with subtask as string and input rates as value.
        """
        # originally it used the rate(numRecordsIn)
        subtask_input_rate_query = f"rate(flink_taskmanager_job_task_operator_numRecordsIn" \
                          f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        subtask_input_rate_data = self.__get_results_from_prometheus(subtask_input_rate_query)
        subtask_input_rate = self.__extract_per_subtask_metrics(subtask_input_rate_data)
        return subtask_input_rate

    def getSubtaskOutputRateMetrics(self) -> dict[str, int]:
        """
        Get output rates of all subtasks
        :return: Dictionary with subtask as string and output rates as value.
        """
        subtask_output_rate_query = f"avg_over_time(flink_taskmanager_job_task_numRecordsOutPerSecond" \
                           f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        subtask_output_rate_data = self.__get_results_from_prometheus(subtask_output_rate_query)
        subtask_output_rates = self.__extract_per_subtask_metrics(subtask_output_rate_data)
        return subtask_output_rates

    def get_subtask_busy_time_metrics(self) -> dict[str, float]:
        """
        Get the busy-times of very subtask/operator.
        :return: Dictionary with subtask as string and busytime as value.
        """
        subtask_busy_time_query = f"avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond" \
                                  f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])/1000"
        subtask_busy_time_data = self.__get_results_from_prometheus(subtask_busy_time_query)
        subtask_busy_time = self.__extract_per_subtask_metrics(subtask_busy_time_data)
        return subtask_busy_time

    # Get single value
    @staticmethod
    def __extract_all_values(prometheusResponse) -> [str]:
        """
        Extract all values from a prometheusResponse and return them as a list.
        :param prometheusResponse: Response from prometheus to get information from
        :return: List of [value]
        """
        metrics = prometheusResponse.json()["data"]["result"]
        values = []
        for results in metrics:
            values.append(results["value"][1])
        return values

    # Parallelism gathering
    def get_all_total_taskslots(self) -> [int]:
        """
        Get the total taskslots of all jobs running in the cluster.
        This can be used to determine the amount of running taskmanagers when running in Reactive mode.
        :return: A directory with {operator, currentParallelism}
        """
        total_taskslots_query = f"flink_jobmanager_taskSlotsTotal"
        total_taskslots_data = self.__get_results_from_prometheus(total_taskslots_query)
        total_taskslots = self.__extract_all_values(total_taskslots_data)
        total_taskslots_ints = list(map(lambda v: int(v), total_taskslots))
        return total_taskslots_ints
