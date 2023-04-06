import math
from abc import ABC
import time

from .DhalionConfigurations import DhalionConfigurations
from .DhalionApplicationManager import DhalionApplicationManager

from common import ScaleManager
from common import Autoscaler


class Dhalion(Autoscaler, ABC):
    desired_parallelisms: {str, int}
    configurations: DhalionConfigurations
    application_manager: DhalionApplicationManager
    scale_manager: ScaleManager
    operators: [str]
    topology: [(str, str)]

    def __init__(self):
        self.configurations = DhalionConfigurations()
        self.application_manager = DhalionApplicationManager(self.configurations)
        self.scale_manager: ScaleManager = ScaleManager(self.configurations, self.application_manager)

    def initialize(self):
        """
        Initialize Dhalion initializing the remaining application connections and fetching non-changing experiment
        settings.
        """
        self.application_manager.initialize()
        self.operators = self.application_manager.jobmanagerManager.getOperators()
        self.topology = self.application_manager.gather_topology(False)
        print(f"Found operators: '{self.operators}' with topology: '{self.topology}'")
        current_parallelisms = self.application_manager.fetch_current_operator_parallelism_information(known_operators=self.operators)
        print(f"Found initial parallelisms: '{current_parallelisms}'")
        self.desired_parallelisms = current_parallelisms

    def set_desired_parallelism(self, operator: str, desired_parallelism: int) -> None:
        """
        Set the desired parallelism of operator {operator}
        """
        self.desired_parallelisms[operator] = desired_parallelism

    def get_desired_parallelisms(self) -> dict[str, int]:
        """
        Get the current desired parallelism.
        """
        return self.desired_parallelisms

    def calculate_operator_scale_up_factor(self, operator: str, backpressure_time_metrics: {str, float}, topology: (str, str)) \
            -> float:
        """
        Calculate the scaleUpFactor for operator {operator}.
        The calculations are based on the backpressureTimeMetrics and the current topology.
        ScaleUp factor is calculated in the following way:
        - Get backpressure_times of all upstream operators of {operator}
        - Pick maximum backpressure_time as backpressureTime
        - scaleUpFactor = 1 + (backpressureTime / (1 - backpressureTime)
        :param backpressure_time_metrics: A directory of backpressure_times with operator names as keys.
        :param operator: Operator to calculate scale-up factor for
        :param topology: Topology of the current query. Should contain a list of directed edges.
        :return: ScaleUpFactor
        """
        print(f"Calculating scale factor of regular operator: {operator}")
        backpressure_values = []
        for op1, op2 in topology:
            if op2 == operator:
                # if op1 is in backpressure time metrics
                if self.application_manager.operator_in_dictionary(op1, backpressure_time_metrics, "backpressure time metrics"):
                    # add backpressure time metric of op1 to backpressure_values
                    backpressure_values.append(backpressure_time_metrics[op1])

        if backpressure_values:
            # backpressure_time of operator is the maximum backpressure value
            backpressure_time = max(backpressure_values)
        else:
            print(f"Warning: no backpressure values found for victims of slow operator '{operator}'")
            backpressure_time = 0

        # scaleUpFactor is not allowed to be larger than 10 and cannot be smaller than 1
        backpressure_time = min(0.9, backpressure_time)
        normal_time = 1 - backpressure_time
        scale_up_factor = 1 + backpressure_time / normal_time
        return scale_up_factor

    def calculate_source_operator_scale_up_factor(self, operator, source_operator_pending_records_rate_metrics,
                                                  source_operator_consumed_records_rate_metrics) -> float:
        """
        Calculate the scale-up factor of a source operator.
        This is done with the following formula:
        Scaleup factor = pending_records_rate / source_input_rate
        The scaleup factor cannot be larger than 10 and cannot be smaller than 1
        :param operator: operator to determine scale_up_factor for
        :param source_operator_pending_records_rate_metrics: Pending record rates of every source operator (records / second)
        :param source_operator_consumed_records_rate_metrics: Consuemd record rates of every source operator (records / second)
        :return: scale_up_factor of operator.
        """
        print(f"Calculating scale factor of source operator: {operator}")
        if self.application_manager.operator_in_dictionary(operator, source_operator_pending_records_rate_metrics, "pending rec/s") and \
                self.application_manager.operator_in_dictionary(operator, source_operator_consumed_records_rate_metrics, "consumed rec/s"):
            pending_records_rate = source_operator_pending_records_rate_metrics[operator]
            consumed_records_rate = source_operator_consumed_records_rate_metrics[operator]

            # Prevent division by 0 errors
            if consumed_records_rate == 0:
                consumed_records_rate = 1

            # Calculate scale-up factor
            scale_up_factor = 1 + pending_records_rate / consumed_records_rate

            # scale_up_factor is not allowed to be larger than 10 and cannot be smaller than 1
            scale_up_factor = max(1, scale_up_factor)
            return scale_up_factor

    def calculate_desired_parallelism(self, operator: str, current_parallelisms: {str, int}, scale_factor: float) -> int:
        """
        Get the desired parallelisms of an operator based on its current parallelism, a scaling facotr and whether it is
        scaling up or down.
        :param operator: Operator to determine the desired parallelism for.
        :param current_parallelisms: The current parallelism of the operator
        :param scale_factor: The scaling factor to scale by (multiplier).
        :return: The desired parallelisms of the operator
        """
        if self.application_manager.operator_in_dictionary(operator, current_parallelisms, "current parallelisms"):
            # get current parallelism
            current_parallelism = current_parallelisms[operator]
            # If scale-factor >= 1, round up
            if scale_factor >= 1:
                desired_parallelism = math.ceil(current_parallelism * scale_factor)
            # if scale-factor < 1, round down
            else:
                desired_parallelism = math.floor(current_parallelism * scale_factor)
            # desired_parallelism is 1 or higher
            desired_parallelism = max(desired_parallelism, 1)
            return desired_parallelism
        else:
            # Signal an error in determining the desired parallelism
            return -1

    def run_autoscaler_iteration(self):
        """
        Single Dhalion Autoscaler Iterator. It follows the following pseudo code:
        Wait for monitoring period
        If backpressure exists:
            If backpressure cannot be contributed to slow instances or skew (it can't:
                Find bottleneck causing the backpressure
                Scale up bottleneck
        else if no backpressure exists:
            if for all instances of operator, the average number of pending packets is almost 0:
                scale down with {underprovisioning system}
        if after scaling down, backpressure is observed:
            undo action and blacklist action
        :return: None
        """
        print("\nStarting new Dhalion iteration.")
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Get all operators causing backpressure. No operators are provided if there is no backpressure
        bottleneck_operators: [str] = self.application_manager.gather_bottleneck_operators(
            self.topology, kafka_source_is_backpressured_threshold=self.configurations.DHALION_KAFKA_LAG_RATE_TO_BE_BACKPRESSURED_THRESHOLD)

        # Get current parallelisms
        current_parallelisms: {str, int} = self.application_manager.fetch_current_operator_parallelism_information(
            known_operators=self.operators)

        # Print metrics
        self.application_manager.print_metrics({"current parallelisms": current_parallelisms, "bottleneck_operators": bottleneck_operators})

        # If backpressure exist, assume unhealthy state and investigate scale up possibilities
        if bottleneck_operators:
            print(f"Backpressure is detected: system is in a unhealthy state. Investigating scale-up possibilities.")

            # Fetching metrics: operator_backpressure_times, source_pending_record_rates, source_consumed_record_rates
            operator_backpressure_time_metrics: {str, float} = self.application_manager.gather_backpressure_time_metrics(
                monitoring_period_seconds=self.configurations.ITERATION_PERIOD_SECONDS)
            source_operator_pending_records_rate_metrics = self.application_manager.gather_source_operator_pending_record_metrics()
            source_operator_consumed_records_rate_metrics = self.application_manager.gather_source_operator_consumed_records_rate_metrics()

            # Print metrics
            self.application_manager.print_metrics({
                "Backpressure-times": operator_backpressure_time_metrics,
                "Source-pending-records-rate": source_operator_pending_records_rate_metrics,
                "Source-consumed-records-rate": source_operator_consumed_records_rate_metrics,
            })

            # For every operator causing backpressure
            for operator in bottleneck_operators:
                # If operator is a source
                if self.configurations.experimentData.operator_is_a_source(operator):
                    # Calculate operatorScaleUpFactor for a source
                    operator_scale_up_factor = self.calculate_source_operator_scale_up_factor(
                        operator, source_operator_pending_records_rate_metrics, source_operator_consumed_records_rate_metrics)
                else:
                    # Calculate operatorScaleUpFactor for a regular operator
                    operator_scale_up_factor = self.calculate_operator_scale_up_factor(
                        operator, operator_backpressure_time_metrics, self.topology)

                # Get desired parallelism
                operator_desired_parallelism = self.calculate_desired_parallelism(operator, current_parallelisms, operator_scale_up_factor)
                print(f"Determined a scale-up factor of {operator_scale_up_factor} for operator {operator}, which resulted"
                      f" in desired parallelism {operator_desired_parallelism}")

                # Save desired parallelism
                self.set_desired_parallelism(operator, operator_desired_parallelism)

        # If no backpressure exists, assume a healthy state
        else:
            print(
                "No backpressure detected, system is in an healthy state. Investigating scale-down possibilities.")
            # Get information about input buffers of operators
            input_queue_metrics = self.application_manager.gather_buffers_in_usage_metrics()
            pending_records_metrics = self.application_manager.gather_source_operator_pending_record_metrics()

            self.application_manager.print_metrics({"input queue metrics": input_queue_metrics,
                                                   "pending records metrics": pending_records_metrics})

            # For every operator
            for operator in self.operators:
                # Check if input queue buffer is almost empty
                if self.configurations.experimentData.operator_is_a_source(operator):
                    operator_has_no_lag = self.application_manager.pending_records_is_close_to_zero(
                        operator, pending_records_metrics, self.configurations.DHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD)
                    if operator_has_no_lag:
                        print(f"Source-operator {operator} is not experiencing any lag. Scaling down operator")
                    else:
                        print(f"Source-operator {operator} is experiencing lag. Source-operator is not scaled down.")
                else:
                    operator_has_no_lag = self.application_manager.queue_size_is_close_to_zero(
                        operator, input_queue_metrics, self.configurations.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD)
                    if operator_has_no_lag:
                        print(f"Operator {operator} is not experiencing any lag. Scaling down operator")
                    else:
                        print(f"Operator {operator} is experiencing lag. Operator is not scaled down.")

                if operator_has_no_lag:
                    # Scale down with SCALE_DOWN_FACTOR
                    # Get desired parallelism
                    operator_desired_parallelism = self.calculate_desired_parallelism(operator, current_parallelisms,
                                                                                      self.configurations.DHALION_SCALE_DOWN_FACTOR)

                    self.set_desired_parallelism(operator, operator_desired_parallelism)

        # Manage scaling actions
        desired_parallelisms = self.get_desired_parallelisms()

        # Print parallelisms
        self.application_manager.print_metrics({"Current parallelisms": current_parallelisms, "Desired parallelisms": desired_parallelisms})

        # Perform scaling actions
        self.scale_manager.perform_scale_operations(current_parallelisms, desired_parallelisms)
