from common import ApplicationManager


class DhalionApplicationManager(ApplicationManager):

    def gather_operator_backpressure_status_metrics(self) -> dict[str, bool]:
        """
        Get the backpressure status metrics of all operators from prometheus.
        This is used to detect backpressure in the system and to find the operator causing the backpressure.
        """
        return self.prometheusManager.get_operator_backpressure_status_metrics()

    def gather_source_operator_pending_record_metrics(self) -> dict[str, float]:
        """
        Get the rate of change in pending records from prometheus.
        This is used to determine the scale-factor of a source operator.
        """
        return self.prometheusManager.get_source_operator_pending_records_rate()

    def gather_source_operator_consumed_records_rate_metrics(self) -> dict[str, float]:
        """
        Get the rate of change in consumed records from prometheus.
        This is used to determine the scale-factor of a source operator.
        """
        return self.prometheusManager.get_source_operator_consumed_records_rate()

    def gather_source_operator_backpressure_status_metrics(self, kafka_source_is_backpressured_threshold: int) -> dict[str, bool]:
        """
        Get a list of source operators, whose upstream kafka source is experiencing backpressure.
        An upstream kafka source is experiencing backpressure if its pendingRecordsRate is positive
        :param kafka_source_is_backpressured_threshold: Minimal amount of lag (records in kafka queue) to consider the
        kafka source backpressured.
        :return: List of source operators, whose upstream kafka source is experiencing backpressure.
        """
        return self.prometheusManager.get_source_operator_backpressure_status_metrics(kafka_source_is_backpressured_threshold)

    def gather_backpressure_time_metrics(self, monitoring_period_seconds=None) -> dict[str, float]:
        """
        Get the backpressure-time metrics from prometheus. If a monitoring period is provided, we aggregate the
        backpressure-time over that period. If not provided, use the METRIC_AGGREGATION_PERIOD_SECONDS configuration.
        """
        if monitoring_period_seconds is not None:
            return self.prometheusManager.get_operator_backpressure_time_metrics(
                monitoringPeriodSeconds=monitoring_period_seconds)
        else:
            return self.prometheusManager.get_operator_backpressure_time_metrics()

    def gather_buffers_in_usage_metrics(self) -> dict[str, float]:
        """
        Get the buffersInUsage metrics from Prometheus.
        """
        return self.prometheusManager.get_operator_average_buffer_in_usage_metrics()

    def queue_size_is_close_to_zero(self, operator: str, input_queue_metrics: {str, float}, buffer_usage_close_to_zero_threshold: float) \
            -> bool:
        """
        Check whether the queue-size of operator {operator} is close to zero.
        This is done by taking the inputQueue size of the operator and check whether it is smaller than
        buffer_usage_close_to_zero_threshold
        :param operator: Operator to check the queueSize for
        :param input_queue_metrics: Directory of inputQueueMetrics with OperatorName as key and its inputQueueSize as
        value
        :param buffer_usage_close_to_zero_threshold: threshold indicating hwo small the buffer usage should be for it to be considered
        'empty'
        :return: Whether the operator's input Queuesize is close to zero
        """
        if self.operator_in_dictionary(operator, input_queue_metrics, "input queue metrics"):
            return input_queue_metrics[operator] <= buffer_usage_close_to_zero_threshold
        else:
            return False

    def pending_records_is_close_to_zero(self, source_operator, pending_records_metrics: {str, int}, kafka_lag_close_to_zero_threshold) \
            -> bool:
        """
        Check whether the pending records of sourceOperator {source_operator} is close to zero.
        This is done by taking the total amount of pendingRecords and check whether it is smaller than
        kafka_lag_close_to_zero_threshold.
        :param source_operator: operator to check whether its pendingRecords is close to zero
        :param pending_records_metrics: Directory of sourceOperators and the amount of pending records for this operator
        :param kafka_lag_close_to_zero_threshold: maximum amount of lag for the kafka queue to be considered empty
        :return: Whether the kafka lag corresponding to the sourceOperator is close to zero.
        """
        if self.operator_in_dictionary(source_operator, pending_records_metrics, "pending records metrics"):
            return pending_records_metrics[source_operator] <= kafka_lag_close_to_zero_threshold
        else:
            return False
