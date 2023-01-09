from common import ApplicationManager


class HPAVargaApplicationManager(ApplicationManager):


    def gather_utilization_metrics(self) -> dict[str, float]:
        """
        1 - (avg(flink_taskmanager_job_task_idleTimeMsPerSecond) by (<<.GroupBy>>) / 1000)
        :return:
        """
        idle_timeMetrics: {str, float} = self.prometheusManager.get_operator_idle_time_per_second()
        utilizationMetrics: {str, float} = {}
        for operator in idle_timeMetrics.keys():
            idle_time = idle_timeMetrics[operator]
            utilizationMetrics[operator] = 1 - idle_time
        return utilizationMetrics


    def gather_relative_lag_change_metrics(self, operators: [str], topology: [(str, str)], kafka_source_is_backpressured_threshold: int,
                                           lag_derivative_period_seconds: int) -> dict[str,  int]:
        """
        We need to gather the relative lag change for each operator. This is done with the following method:
        If an operator is causing backpressure in an operator, we sum the kafka_lag and kafka_lag_derivative from the
        sources the operator is receiving data from. This data is then used to calculate the relative lag change with
        the following formula: relative_lag_change = 1 + derivative(total_lag) / input_Rate
        @param operators: operators present in the current topology.
        @param topology: the topology of the current job.
        @param kafka_source_is_backpressured_threshold: threshold in terms of amount of records present in the kafka
        @param lag_derivative_period_seconds: period to calculate the derivative of the lag over.
        queue to determine whether the kafka source is backpressured.
        @:return A dictionary with as key the operator names and as value the relative_lag_change.
        """
        # list of operators causing backpressure
        backpressure_causing_operators = self.gather_bottleneck_operators(topology, kafka_source_is_backpressured_threshold)

        # Initiate relative_lag_change_metrics (result) as a dictionary with all operators having a relative_lag_change
        # of -1 (will only consider utilization at that point).
        relative_lag_change_metrics = {}
        for operator in operators:
            # Set default value to not consider the relative lag change
            relative_lag_change_metrics[operator] = -1

        # If we have backpressure
        if backpressure_causing_operators:

            # Fetch metrics from prometheus: The lag per source and the derivative of the lag per source
            source_operator_consumed_rate = self.prometheusManager.get_source_operator_consumed_records_rate()
            source_operator_pending_records_derivative = self.prometheusManager.get_source_operator_pending_records_derivative(
                derivative_period_seconds=lag_derivative_period_seconds)

            # Print the metrics we fetched from prometheus
            self.print_metrics({
                "Backpressure causing operators": backpressure_causing_operators,
                "Source operator consumed rate (totalRate)": source_operator_consumed_rate,
                "Source operator pending records (deriv(totalLag))": source_operator_pending_records_derivative
            })

            # For every operator that is causing backpressure
            for backpressure_causing_operator in backpressure_causing_operators:
                # Determine the lag and the derivative the lag the operator is causing in the source
                total_rate = 0
                derivative_total_lag = 0

                # Get a list of all sources the operator is causing backpressure in.
                source_operators: [str] = self.configurations.experimentData.gather_source_operators_of_operator(
                    backpressure_causing_operator, topology)

                # For every source the operator is causing backpressure in
                for source_operator in source_operators:
                    # Add the source's lag to the operator_consumed_rate
                    if not self.operator_in_dictionary(source_operator, source_operator_consumed_rate, "source_operator_consumed_rate"):
                        continue
                    total_rate += source_operator_consumed_rate[source_operator]

                    # Add the source's lag derivative to operator_lag_derivative
                    if not self.operator_in_dictionary(source_operator, source_operator_pending_records_derivative,
                                                       "source_operator_pending_records_derivative"):
                        continue
                    derivative_total_lag += source_operator_pending_records_derivative[source_operator]

                # Prevent division by zero in the calculation of relative_lag_change
                if total_rate == 0:
                    total_rate = 1

                relative_lag_change = 1 + derivative_total_lag / total_rate

                print(f"Found the following data of {backpressure_causing_operator}. Total rate: {total_rate} "
                      f"Derivative(totalLag): {derivative_total_lag} relative lag change: {relative_lag_change}")

                # Set the relative_lag_change of the backpressure causing operator
                relative_lag_change_metrics[backpressure_causing_operator] = relative_lag_change

        return relative_lag_change_metrics

