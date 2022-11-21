from common import MetricsGatherer


class DS2MetricsGatherer(MetricsGatherer):

    def gatherTopicKafkaInputRates(self) -> {str, int}:
        topicKafkaInputRates = self.prometheusMetricGatherer.getTopicKafkaInputRates()
        return topicKafkaInputRates

    def gatherOperatorKafkaLag(self) -> {str, int}:
        operatorKafkaLag = self.prometheusMetricGatherer.getOperatorKafkaLag()
        return operatorKafkaLag


    def gatherSubtaskBusyTimes(self) -> {str, float}:
        busyTime = self.prometheusMetricGatherer.getSubtaskBusyTimeMetrics()
        return busyTime

    def gatherSubtaskTrueProcessingRates(self, subtaskInputRates: {str, int}=None, subtaskBusyTimes: {str, float}=None)\
            -> {str, float}:
        if not subtaskInputRates:
            subtaskInputRates = self.gatherSubtaskInputRates()
        if not subtaskBusyTimes:
            subtaskBusyTimes = self.gatherSubtaskBusyTimes()

        subtaskTrueProcessingRates = {}
        for subtask in subtaskInputRates.keys():
            if subtask in subtaskBusyTimes:
                subtaskInputRate = subtaskInputRates[subtask]
                subtaskBusyTime = subtaskBusyTimes[subtask]
                subtaskTrueProcessingRate = (subtaskInputRate / subtaskBusyTime)
                subtaskTrueProcessingRates[subtask] = subtaskTrueProcessingRate
            else:
                print(f"Error: subtask {subtask} of subtaskInputRates '{subtaskInputRates}' not found in "
                      f"subtaskBusyTimes '{subtaskBusyTimes}' ")
        return subtaskTrueProcessingRates

    def gatherSubtaskTrueOutputRates(self, subtaskOutputRates: {str, int}=None, subtaskBusyTimes: {str, int}=None) \
            -> {str, int}:
        if not subtaskOutputRates:
            subtaskOutputRates = self.gatherSubtaskOutputRates()
        if not subtaskBusyTimes:
            subtaskBusyTimes = self.prometheusMetricGatherer.getSubtaskBusyTimeMetrics()

        subtaskTrueOutputRates = {}
        for subtask in subtaskOutputRates.keys():
            if subtask in subtaskBusyTimes:
                subtaskOutputRate = subtaskOutputRates[subtask]
                subtaskBusyTime = subtaskBusyTimes[subtask]
                if subtaskBusyTime != 0:
                    subtaskTrueOutputRates[subtask] = subtaskOutputRate / subtaskBusyTime
                else:
                    subtaskTrueOutputRates[subtask] = 0
            else:
                print(f"Error: subtask '{subtask}' was found in subtaskOutputRates '{subtaskOutputRates}' found in "
                      f"subtaskBusyTimes '{subtaskBusyTimes}'")
        return subtaskTrueOutputRates

    def gatherSubtaskInputRates(self) -> {str, int}:
        subtaskInputRates = self.prometheusMetricGatherer.getSubtaskInputRateMetrics()
        return subtaskInputRates

    def gatherSubtaskOutputRates(self) -> {str, int}:
        subtaskOutputRates = self.prometheusMetricGatherer.getSubtaskOutputRateMetrics()
        return subtaskOutputRates
