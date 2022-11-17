from common import MetricsGatherer


class DhalionMetricsGatherer(MetricsGatherer):

    def gatherBackpressureStatusMetrics(self):
        return self.prometheusMetricGatherer.getBackpressureStatusMetrics()

    def gatherBackpressureTimeMetrics(self, monitoringPeriodSeconds=None):
        if monitoringPeriodSeconds is not None:
            return self.prometheusMetricGatherer.getBackpressureTimeMetrics(
                monitoring_period_seconds=monitoringPeriodSeconds
            )
        else:
            return self.prometheusMetricGatherer.getBackpressureTimeMetrics()

    def gatherBuffersInUsageMetrics(self):
        return self.prometheusMetricGatherer.getMaximumBuffersInUsageMetrics()

    def isSystemBackpressured(self, backpressureStatusMetrics: {str, bool}=None) -> bool:
        """
        Check whether one of the operators is experiencing backpressure
        :return: Whether at leas tone of the operators is experiencing backpressure.
        """
        if not backpressureStatusMetrics:
            backpressureStatusMetrics = self.gatherBackpressureStatusMetrics()
        isSystemBackpressured: bool = True in backpressureStatusMetrics.values()
        return isSystemBackpressured

    def gatherBottleneckOperators(self, backpressureStatusMetrics: {str, bool}=None,
                                  topology: [(str, str)] = None) -> [str]:
        """
        Get all operators that are causing backpressure in the system.
        An operator is said to cause backpressure if it is not experiencing backpressure itself, but at least one of its
        upstream operators is.
        :param backpressureStatusMetrics: Metrics indicating whether operators are experiencing backpressure
        :param topology: The topology of the system, containing directed edges (lop -> rop)
        :return: A list of operators causing backpressure.
        """
        if not backpressureStatusMetrics:
            backpressureStatusMetrics = self.gatherBackpressureStatusMetrics()
        if not topology:
            topology = self.jobmanagerMetricGatherer.getTopology()

        bottleNeckOperatorsSet: set = set()
        for lOperator, rOperator in topology:
            if lOperator not in backpressureStatusMetrics:
                print(
                    f"Error: left operator '{lOperator}' of topology '{topology}' not found in backpressure status "
                    f"metrics '{backpressureStatusMetrics}'.")
                continue
            if rOperator not in backpressureStatusMetrics:
                print(
                    f"Error: right operator '{rOperator}' of topology '{topology}' not found in backpressure status "
                    f"metrics '{backpressureStatusMetrics}'.")
                continue

            if backpressureStatusMetrics[lOperator]:
                if not backpressureStatusMetrics[rOperator]:
                    bottleNeckOperatorsSet.add(rOperator)

        return list(bottleNeckOperatorsSet)
