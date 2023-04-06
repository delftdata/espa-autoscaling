from common import ApplicationManager


class DS2ApplicationManager(ApplicationManager):



    def gather_topic_kafka_input_rates(self) -> dict[str, int]:
        """
        Get the input_rate of the kafka rates. This is the input_rate of the data sent from the generator to kafka
        :return: Dictionary with as str the topic of the input_rate and as value the input_rate.
        """
        topicKafkaInputRates = self.prometheusManager.get_topic_kafka_input_rates()
        return topicKafkaInputRates

    def gather_topic_kafka_lag(self) -> dict[str, float]:
        """
        Get the total lag per topic.
        Function is not yet used, but can be used for a potential improvement of DS2.
        :return: {topic_name: str -> total_topic_lag}
        """
        operator_kafka_lag = self.prometheusManager.get_operator_kafka_lag()
        topic_lag = {}
        for operator, value in operator_kafka_lag.items():
            topicName = self.configurations.experimentData.get_topic_from_operator_name(operator, print_error=False)
            if topicName:
                topic_lag[topicName] = float(value)
            else:
                print(f"Error: could not determine topic corresponding to '{operator}' not found")
        return topic_lag

    def gather_subtask_true_processing_rates(self, subtask_input_rates: dict[str, int] = None, subtask_busy_times: dict[str, float] = None,
                                             maximum_busy_time: float = 1.0) -> dict[str, int]:
        """
        Get the true processing rate of every operator (subtask). This is calculated by dividing the input rate with the operators busy
        time.
        :param subtask_input_rates: Input rate of every operator (subtask).
        :param subtask_busy_times: Busy time of every operator (subtask).
        :param maximum_busy_time: Maximum value of the busy time. Used to get an accurate estimation of the maximum busy time of the
        operator. Value should be between 0 and 1 for correct result. subtask_busy_time = subtask_busy_time / maximum_busy_time
        :return: ictionary with as str the operator's (subtask's) name and as value the true processing rate.
        """
        if not subtask_input_rates:
            subtask_input_rates = self.gather_subtask_input_rates()
        if not subtask_busy_times:
            subtask_busy_times = self.prometheusManager.get_subtask_busy_time_metrics()

        subtask_true_processing_rates = {}
        for subtask in subtask_input_rates.keys():
            if self.operator_in_dictionary(subtask, subtask_busy_times, f"subtask_busy_times (subtask from subtask_input_rates "
                                                                        f"{subtask_input_rates}"):
                subtask_input_rate = subtask_input_rates[subtask]
                subtask_busy_time = subtask_busy_times[subtask]

                # Correct for possibly wrong assumption of maximum busy time being 1.0
                corrected_subtask_busy_time = subtask_busy_time / maximum_busy_time

                if corrected_subtask_busy_time != 0:
                    subtask_true_processing_rate = (subtask_input_rate / corrected_subtask_busy_time)
                else:
                    subtask_true_processing_rate = 0
                subtask_true_processing_rates[subtask] = subtask_true_processing_rate
        return subtask_true_processing_rates

    def gather_subtask_true_output_rates(self, subtask_output_rates: dict[str, int] = None, subtask_busy_times: dict[str, float] = None,
                                         maximum_busy_time: float = 1.0) \
            -> dict[str, int]:
        """
        Get the true output rate of every operator (subtask). This is calculated by dividing the input rate with the operator's busy time.
        :param subtask_output_rates: The output rate of every operator (subtask).
        :param subtask_busy_times: The busy time of every operator (subtask).
        :param maximum_busy_time: Maximum value of the busy time. Used to get an accurate estimation of the maximum busy time of the
        operator. Value should be between 0 and 1 for correct result. subtask_busy_time = subtask_busy_time / maximum_busy_time
        :return: Dictionary with as str the operator's (subtask's) name and as value the true output rate.
        """
        if not subtask_output_rates:
            subtask_output_rates = self.gather_subtask_output_rates()
        if not subtask_busy_times:
            subtask_busy_times = self.prometheusManager.get_subtask_busy_time_metrics()

        subtask_true_output_rates = {}
        for subtask in subtask_output_rates.keys():
            if self.operator_in_dictionary(subtask, subtask_busy_times, f"subtask_busy_times (subtask from subtask_output_rates "
                                                                        f"{subtask_output_rates}"):
                subtask_output_rate = subtask_output_rates[subtask]
                subtask_busy_time = subtask_busy_times[subtask]

                # Correct for possibly wrong assumption of maximum busy time being 1.0
                corrected_subtask_busy_time = subtask_busy_time / maximum_busy_time

                if corrected_subtask_busy_time != 0:
                    subtask_true_output_rates[subtask] = subtask_output_rate / corrected_subtask_busy_time
                else:
                    subtask_true_output_rates[subtask] = 0
        return subtask_true_output_rates

    def gather_subtask_input_rates(self) -> dict[str, int]:
        """
        Get the input rate of every operator (subtask).
        :return: Dictionary with as key the operator's (subtask's) name and as value its input rate.
        """
        subtask_input_rates = self.prometheusManager.get_subtask_input_rate_metrics()
        return subtask_input_rates

    def gather_subtask_output_rates(self) -> dict[str, int]:
        """
        Get the output rate of every operator (subtask)
        :return: Dictionary with as key the operator's (subtask's) name and as value its output rate.
        """
        subtask_output_rates = self.prometheusManager.getSubtaskOutputRateMetrics()
        return subtask_output_rates


    def gather_subtask_busy_times(self) -> dict[str, float]:
        """
        Get the busy_time of every subtask run in the cluster.
        :return: Dictionary with as string the subtask ID and as value the busy time.
        """
        subtask_busy_times = self.prometheusManager.get_subtask_busy_time_metrics()
        return subtask_busy_times
