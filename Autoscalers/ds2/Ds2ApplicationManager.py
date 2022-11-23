from common import ApplicationManager


class DS2ApplicationManager(ApplicationManager):

    def gatherTopicKafkaInputRates(self) -> {str, int}:
        topicKafkaInputRates = self.prometheusManager.getTopicKafkaInputRates()
        return topicKafkaInputRates

    def gatherOperatorKafkaLag(self) -> {str, int}:
        operatorKafkaLag = self.prometheusManager.getOperatorKafkaLag()
        return operatorKafkaLag

    def getTopicKafkaLag(self) -> {str, int}:
        """
        Get the total lag per topic.
        Function is not yet used, but can be used for a potential improvement of DS2.
        :return: {topic_name: str -> total_topic_lag}
        """
        operatorKafkaLag = self.gatherOperatorKafkaLag()
        topicLag = {}
        for operator, value in operatorKafkaLag.items():
            topicName = self.getTopicFromOperatorName(operator)
            if topicName:
                topicLag[topicName] = float(value)
            else:
                print(f"Error: could not determine topic corresponding to '{operator}' not found")
        return topicLag

    def gatherSubtaskBusyTimes(self) -> {str, float}:
        busyTime = self.prometheusManager.getSubtaskBusyTimeMetrics()
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
            subtaskBusyTimes = self.prometheusManager.getSubtaskBusyTimeMetrics()

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
        subtaskInputRates = self.prometheusManager.getSubtaskInputRateMetrics()
        return subtaskInputRates

    def gatherSubtaskOutputRates(self) -> {str, int}:
        subtaskOutputRates = self.prometheusManager.getSubtaskOutputRateMetrics()
        return subtaskOutputRates
