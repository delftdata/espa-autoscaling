import requests

from common import Configurations


class PrometheusMetricGatherer:
    configurations: Configurations

    def __init__(self, configurations: Configurations):
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

    def __extract_per_operator_metrics(self, prometheusResponse):
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

    def __extract_per_taskmanager_metrics(self, prometheusResponse):
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
    def getSumBufferInUsageMetrics(self) -> {str, float}:
        inputBufferUsageSum_query = f"sum(avg_over_time(flink_taskmanager_job_task_buffers_inPoolUsage" \
                                    f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        inputBufferUsageSum_data = self.__getResultsFromPrometheus(inputBufferUsageSum_query)
        inputBufferUsageSum = self.__extract_per_operator_metrics(inputBufferUsageSum_data)
        return inputBufferUsageSum

    def getMaximumBuffersInUsageMetrics(self) -> {str, float}:
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
    def getCurrentParallelismMetrics(self) -> {str, int}:
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
    def getBackpressureTimeMetrics(self, monitoringPeriodSeconds=None) -> {str, float}:
        """
        Get backpressure time of all operators.
        If monitoring_period_seconds is provided, this will be used as a period to gather metrics for.
        Else self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS is used.
        :param monitoring_period_seconds: Optional parameter to determine aggregation period.
        :return:
        """
        gatherPeriod = monitoringPeriodSeconds if monitoringPeriodSeconds else self.configurations.\
            METRIC_AGGREGATION_PERIOD_SECONDS
        backpressure_time_query = f"avg(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond" \
                                  f"[{gatherPeriod}s]) / 1000) by (task_name)"
        backpressure_time_data = self.__getResultsFromPrometheus(backpressure_time_query)
        backpressure_time = self.__extract_per_operator_metrics(backpressure_time_data)
        return backpressure_time

    def getBackpressureStatusMetrics(self) -> {str, bool}:
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

