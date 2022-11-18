from common import MetricsGatherer


class HPAMetricsGathererVarga(MetricsGatherer):

    def gatherUtilizationMetrics(self) -> {str, float}:
        """
        1 - (avg(flink_taskmanager_job_task_idleTimeMsPerSecond) by (<<.GroupBy>>) / 1000)
        :return:
        """
        idle_timeMetrics: {str, float} = self.prometheusMetricGatherer.getOperatorIdleTimePerSecond()
        utilizationMetrics: {str, float} = {}
        for operator in idle_timeMetrics.keys():
            idle_time = idle_timeMetrics[operator]
            utilizationMetrics[operator] = 1 - idle_time
        return utilizationMetrics

    def gatherRelativeLagChangeMetrics(self) -> {str, int}:
        """
        ((
             sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)
             by ( <<.GroupBy >>) - 50000) / (abs(sum(
            flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)
                                             by ( <<.GroupBy >>) - 50000)))*(1 + deriv(
            sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)
                                                                             by ( <<.GroupBy >>)[1
        m: 2
        s]) / sum(
            avg_over_time(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_consumed_rate[1
        m])) by( <<.GroupBy >>))
        """
        # TODO: implement relative lag change metrics
        return self.gatherUtilizationMetrics()

