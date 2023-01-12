from common import ApplicationManager


class DhalionApplicationManager(ApplicationManager):

    def gatherOperatorBackpressureStatusMetrics(self) -> {str, bool}:
        """
        Get the backpressure status metrics of all operators from prometheus.
        This is used to detect backpressure in the system and to find the operator causing the backpressure.
        """
        return self.prometheusManager.getOperatorBackpressureStatusMetrics()

    def gatherOperatorPendingRecordsRateMetrics(self) -> {str, float}:
        """
        Get the rate of change in pending records from prometheus.
        This is used to determine the scale-factor of a source operator.
        """
        return self.prometheusManager.getSourceOperatorPendingRecordsRate()

    def gatherOperatorConsumedRecordsRateMetrics(self) -> {str, float}:
        """
        Get the rate of change in consumed records from prometheus.
        This is used to determine the scale-factor of a source operator.
        """
        return self.prometheusManager.getSourceOperatorConsumedRecordsRate()

    def gatherSourceOperatorBackpressureStatusMetrics(self, kafka_source_is_backpressured_threshold: int) -> {str, bool}:
        """
        Get a list of source operators, whose upstream kafka source is experiencing backpressure.
        An upstream kafka source is experiencing backpressure if its pendingRecordsRate is positive
        """
        sourceOperatorPendingRecordsRateMetrics = self.gatherOperatorPendingRecordsRateMetrics()

        sourceBackpressureStatusMetrics: {str, bool} = {}
        for source, pendingRecordsRate in sourceOperatorPendingRecordsRateMetrics.items():
            # source is backpressured if pendingRecordsRate is larger than threshold
            sourceBackpressureStatusMetrics[source] = pendingRecordsRate > kafka_source_is_backpressured_threshold
        return sourceBackpressureStatusMetrics

    def gatherBackpressureTimeMetrics(self, monitoringPeriodSeconds=None):
        """
        Get the backpressure-time metrics from prometheus. If a monitoring period is provided, we aggregate the
        backpressure-time over that period. If not provided, use the METRIC_AGGREGATION_PERIOD_SECONDS configuration.
        """
        if monitoringPeriodSeconds is not None:
            return self.prometheusManager.getOperatorBackpressureTimeMetrics(
                monitoringPeriodSeconds=monitoringPeriodSeconds)
        else:
            return self.prometheusManager.getOperatorBackpressureTimeMetrics()

    def gatherSourceOperatorPendingRecordMetrics(self):
        """
        Get the total amount of pending records for all source-operators from prometheus.
        """
        return self.prometheusManager.getSourceOperatorPendingRecords()

    def gatherBuffersInUsageMetrics(self):
        """
        Get the buffersInUsage metrics from Prometheus.
        """
        return self.prometheusManager.getOperatorAverageBufferInUsageMetrics()

    def isSystemBackpressured(self, operatorBackpressureStatusMetrics: {str, bool}=None,
                              sourceOperatorBackpressureStatusMetrics: {str, bool}=None) -> bool:
        """
        Check whether one of the operators is experiencing backpressure
        :return: Whether at leas tone of the operators is experiencing backpressure.
        """
        if not operatorBackpressureStatusMetrics:
            operatorBackpressureStatusMetrics = self.gatherOperatorBackpressureStatusMetrics()
        if not sourceOperatorBackpressureStatusMetrics:
            sourceOperatorBackpressureStatusMetrics = self.gatherSourceOperatorBackpressureStatusMetrics()
        isSystemBackpressured: bool = True in operatorBackpressureStatusMetrics.values() or \
                                      True in sourceOperatorBackpressureStatusMetrics.values()
        return isSystemBackpressured

    def gatherBottleneckOperators(self, operatorBackpressureStatusMetrics: {str, bool}=None,
                                  sourceOperatorBackpressureStatusMetrics: {str, bool}=None,
                                  topology: [(str, str)]=None) -> [str]:
        """
        Get all operators that are causing backpressure in the system.
        An operator is said to cause backpressure if it is not experiencing backpressure itself, but at least one of its
        upstream operators is.
        :param operatorBackpressureStatusMetrics: Metrics indicating whether operators are experiencing backpressure
        :param sourceOperatorBackpressureStatusMetrics: Metrics indicating whether operators are causing backpressure in
        the kafka sources
        :param topology: The topology of the system, containing directed edges (lop -> rop)
        :return: A list of operators causing backpressure.
        """
        if not operatorBackpressureStatusMetrics:
            operatorBackpressureStatusMetrics = self.gatherOperatorBackpressureStatusMetrics()
        if not sourceOperatorBackpressureStatusMetrics:
            sourceOperatorBackpressureStatusMetrics = self.gatherSourceOperatorBackpressureStatusMetrics()
        if not topology:
            topology = self.gatherTopology(False)

        bottleNeckOperatorsSet: set = set()
        for lOperator, rOperator in topology:
            if lOperator not in operatorBackpressureStatusMetrics:
                print(f"Error: right operator '{rOperator}' of topology '{topology}' not found in backpressure status "
                      f"metrics '{operatorBackpressureStatusMetrics}'.")
                continue
            if rOperator not in operatorBackpressureStatusMetrics:
                print(
                    f"Error: right operator '{rOperator}' of topology '{topology}' not found in backpressure status "
                    f"metrics '{operatorBackpressureStatusMetrics}'.")
                continue

            # if lOperator is experiencing backpressure
            if operatorBackpressureStatusMetrics[lOperator]:
                # if its downstream operator is not experiencing backpressure
                if not operatorBackpressureStatusMetrics[rOperator]:
                    # its downstream operator is the cause of the backpressure
                    bottleNeckOperatorsSet.add(rOperator)
            # if lOperator is not experiencing backpressure
            else:
                # if lOperator is a source
                if lOperator in sourceOperatorBackpressureStatusMetrics:
                    # if the kafka source corresponding to lOperator is being backpressured
                    if sourceOperatorBackpressureStatusMetrics[lOperator]:
                        # the source lOperator is causing backpressure
                        bottleNeckOperatorsSet.add(lOperator)
        print(list(bottleNeckOperatorsSet))
        return list(bottleNeckOperatorsSet)
