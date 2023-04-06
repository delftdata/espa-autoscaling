import statistics
import time
from abc import ABC

from .HPACPUConfigurations import HPACPUConfigurations
from .HPACPUApplicationManager import HPACPUApplicationManager
from hpa.HPA import HPA
from common import ScaleManager


class HPACPU(HPA, ABC):
    configurations: HPACPUConfigurations
    application_manager: HPACPUApplicationManager
    scale_manager: ScaleManager
    operators: [str]


    def __init__(self):
        self.configurations = HPACPUConfigurations()
        self.application_manager: HPACPUApplicationManager = HPACPUApplicationManager(self.configurations)
        self.scale_manager: ScaleManager = ScaleManager(self.configurations, self.application_manager)


    def initialize(self):
        self.application_manager.initialize()
        self.operators = self.application_manager.jobmanagerManager.getOperators()

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

        print("\nStarting next HPA-CPU iteration.")
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Gather metrics:
        operator_ready_taskmanagers, operator_unready_taskmanagers = self.application_manager.gatherReady_UnReadyTaskmanagerMapping()
        taskmanager_cpu_usages = self.application_manager.prometheusManager.get_taskmanager_jvm_cpu_usage()
        current_parallelisms = self.application_manager.fetch_current_operator_parallelism_information(known_operators=self.operators)

        self.application_manager.print_metrics({
            "ready operators": operator_ready_taskmanagers, "unready operators": operator_unready_taskmanagers,
            "taskmanager_cpu_usages": taskmanager_cpu_usages, "current_parallelisms": current_parallelisms})

        # Per operator, calculate desired parallelism.
        tmp_desired_parallelisms = {}  # save desired parallelisms for debug purposes
        for operator in self.operators:

            # Check if all metrics are available for operator
            if not self.application_manager.operator_in_dictionary(operator, operator_ready_taskmanagers, "ready taskmanagers"):
                continue
            if not self.application_manager.operator_in_dictionary(operator, current_parallelisms, "current parallelisms"):
                continue

            # We only consider 'ready' taskmanagers. Metrics from unready taskmanagers are ignored.
            ready_taskmanagers = operator_ready_taskmanagers[operator]
            unready_taskmanagers = operator_unready_taskmanagers[operator]
            if len(unready_taskmanagers) > 0:
                print(f"Warning: at least one taskmanager is not ready: '{unready_taskmanagers}'")

            # Calculate the scale_factor of the ready taskmanagers
            ready_CPU_usages = self.application_manager.gatherCPUUsageOfTaskmanagers(ready_taskmanagers,
                                                                                     taskmanager_cpu_usages)

            if len(ready_CPU_usages) <= 0:
                print(f"Error: list of ready_CPU_usages is empty: 'ready_CPU_usages'. ")
                print(
                    f"Metrics used: read_taskmanagers: '{ready_taskmanagers}', cpu_usages '{taskmanager_cpu_usages}'")
                continue

            # Get average cpu value and current parallelism of operator
            ready_average_CPU_value = statistics.mean(ready_CPU_usages)
            current_parallelism = current_parallelisms[operator]

            # Calculate operator_scale_factor and the corresponding desired parallelism
            operator_scale_factor = self.calculate_scale_ratio(ready_average_CPU_value, self.configurations.CPU_UTILIZATION_TARGET_VALUE)
            desired_parallelism = self.calculate_desired_parallelism(operator_scale_factor, current_parallelism)

            # save desired parallelism
            self.add_desired_parallelism_for_operator(operator, desired_parallelism)

            # save desired parallelism in list for debug purpose
            tmp_desired_parallelisms[operator] = desired_parallelism

        # Get maximum desired parallelisms from scale-down window
        allMaximumDesiredParallelisms: {str, int} = self.get_all_maximum_parallelisms_from_window(self.operators)
        print(f"Desired parallelisms: {tmp_desired_parallelisms}")
        print(f"Maximum desired parallelisms: {allMaximumDesiredParallelisms}")
        print(f"Current parallelisms: {current_parallelisms}")
        self.scale_manager.perform_scale_operations(current_parallelisms, allMaximumDesiredParallelisms)
