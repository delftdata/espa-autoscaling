from common import ApplicationManager


class DhalionApplicationManager(ApplicationManager):

    def gatherOperatorPendingRecordsMetrics(self) -> {str, float}:
        return self.prometheusManager.getSourceOperatorPendingRecords()

    def gatherOperatorPendingRecordsRateMetrics(self) -> {str, float}:
        return self.prometheusManager.getSourceOperatorPendingRecordsRate()

    def gatherOperatorBackpressureStatusMetrics(self) -> {str, bool}:
        return self.prometheusManager.getOperatorBackpressureStatusMetrics()

    def gatherSourceOperatorBackpressureStatusMetrics(self) -> {str, bool}:
        sourceOperatorPendingRecordsRateMetrics = self.gatherOperatorPendingRecordsRateMetrics()

        sourceBackpressureStatusMetrics: {str, bool} = {}
        for source, pendingRecordsRate in sourceOperatorPendingRecordsRateMetrics.items():
            # source is backpressured if pendingRecordsRate is positive (increasing)
            sourceBackpressureStatusMetrics[source] = pendingRecordsRate > 0
        return sourceBackpressureStatusMetrics

    def gatherBackpressureTimeMetrics(self, monitoringPeriodSeconds=None):
        if monitoringPeriodSeconds is not None:
            return self.prometheusManager.getOperatorBackpressureTimeMetrics(
                monitoringPeriodSeconds=monitoringPeriodSeconds)
        else:
            return self.prometheusManager.getOperatorBackpressureTimeMetrics()

    def gatherBuffersInUsageMetrics(self):
        return self.prometheusManager.getOperatorMaximumBuffersInUsageMetrics()

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
