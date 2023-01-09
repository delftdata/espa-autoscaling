import time
from abc import ABC

from .HPAVargaConfigurations import HPAVargaConfigurations
from .HPAVargaApplicationManager import HPAVargaApplicationManager
from hpa.HPA import HPA
from common import ScaleManager


class HPAVarga(HPA, ABC):
    configurations: HPAVargaConfigurations
    applicationManager: HPAVargaApplicationManager
    scaleManager: ScaleManager
    operators: [str]
    topology: [(str, str)]

    def __init__(self):
        self.configurations = HPAVargaConfigurations()
        self.applicationManager: HPAVargaApplicationManager = HPAVargaApplicationManager(self.configurations)
        self.scaleManager: ScaleManager = ScaleManager(self.configurations, self.applicationManager)

    def initialize(self):
        self.applicationManager.initialize()
        self.operators = self.applicationManager.jobmanagerManager.getOperators()
        self.topology = self.applicationManager.gather_topology(False)

    def run_autoscaler_iteration(self):
        """
        Perform a single HPA iteration.
        A HPA iteration consists of the following steps:
        1. Gather metrics
        2. Calculate desired parallelism
        3. Add desired parallelisms to scale-down window
        4. Fetch maximum parallelism from window and scale operators with a different desired parallelism than current
        parallelism
        :return: None
        """

        print("\nStarting next HPA-Varga iteration.")
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Gather metrics:
        current_parallelisms = self.applicationManager.fetch_current_operator_parallelism_information(known_operators=self.operators)
        operator_utilization_metrics = self.applicationManager.gather_utilization_metrics()
        operator_relative_lag_change_metrics = self.applicationManager.gather_relative_lag_change_metrics(
            self.operators, self.topology,
            self.configurations.HPA_VARGA_MINIMUM_KAFKA_LAG_RATE_WHEN_BACKPRESSURED_THRESHOLD,
            self.configurations.HPA_VARGA_DERIVATIVE_PERIOD_SECONDS
        )

        # Calculate desired parallelism per operator
        tmp_desired_parallelisms = {}  # save desired parallelisms for debug purposes
        for operator in self.operators:
            if not self.applicationManager.operator_in_dictionary(operator, operator_utilization_metrics, "utilization metrics"):
                continue
            if not self.applicationManager.operator_in_dictionary(operator, operator_relative_lag_change_metrics, "relative lag change "
                                                                                                                  "metrics"):
                continue

            current_parallelism = current_parallelisms[operator]

            utilization = operator_utilization_metrics[operator]
            utilization_scale_factor = self.calculate_scale_ratio(utilization, self.configurations.HPA_VARGA_UTILIZATION_TARGET_VALUE)

            relative_lag_change = operator_relative_lag_change_metrics[operator]
            relative_lag_change_scale_factor = self.calculate_scale_ratio(relative_lag_change,
                                                                          self.configurations.HPA_VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE, )

            # Determine desired parallelism and add to scale-down-window
            operator_scale_factor = max(utilization_scale_factor, relative_lag_change_scale_factor)
            desired_parallelism = self.calculate_desired_parallelism(operator_scale_factor, current_parallelism)
            self.add_desired_parallelism_for_operator(operator, desired_parallelism)

            # save desired parallelism in list for debug purpose
            tmp_desired_parallelisms[operator] = desired_parallelism

        # Get maximum desired parallelisms from scale-down window
        maximum_desired_parallelisms: {str, int} = self.get_all_maximum_parallelisms_from_window(self.operators)
        print(f"Desired parallelisms: {tmp_desired_parallelisms}")
        print(f"Maximum desired parallelisms: {maximum_desired_parallelisms}")
        print(f"Current parallelisms: {current_parallelisms}")
        self.scaleManager.perform_scale_operations(current_parallelisms, maximum_desired_parallelisms)
