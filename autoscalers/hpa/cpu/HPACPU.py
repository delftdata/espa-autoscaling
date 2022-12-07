import statistics
import time

from .HPACPUConfigurations import HPACPUConfigurations
from .HPACPUApplicationManager import HPACPUApplicationManager
from hpa.HPA import HPA
from common import ScaleManager


class HPACPU(HPA):
    configurations: HPACPUConfigurations
    metricsGatherer: HPACPUApplicationManager
    scaleManager: ScaleManager
    operators: [str]


    def __init__(self):
        self.configurations = HPACPUConfigurations()
        self.metricsGatherer: HPACPUApplicationManager = HPACPUApplicationManager(self.configurations)
        self.scaleManager: ScaleManager = ScaleManager(self.configurations, self.metricsGatherer)


    def setInitialMetrics(self):
        self.operators = self.metricsGatherer.jobmanagerManager.getOperators()


    def runAutoscalerIteration(self):
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
        operator_ready_taskmanagers, operator_unready_taskmanagers = self.metricsGatherer. \
            gatherReady_UnReadyTaskmanagerMapping()
        taskmanager_cpu_usages = self.metricsGatherer.prometheusManager.getTaskmanagerJVMCPUUSAGE()
        currentParallelisms = self.metricsGatherer.fetchCurrentOperatorParallelismInformation(
            knownOperators=self.operators)

        # Per operator, calculate desired parallelism.
        desiredParallelisms = {}  # save desired parallelisms for debug purposes
        for operator in self.operators:

            # Check if all metrics are available for operator
            if operator not in operator_ready_taskmanagers:
                print(f"Error: operator '{operator}' not found in operator_ready_taskmanagers '"
                      f"{operator_ready_taskmanagers}'")
                continue
            if operator not in currentParallelisms:
                print(f"Error: operator '{operator}' not found in current parallelisms '{currentParallelisms}'")
                continue

            # We only consider 'ready' taskmanagers. Metrics from unready taskmanagers are ignored.
            ready_taskmanagers = operator_ready_taskmanagers[operator]
            unready_taskmanagers = operator_unready_taskmanagers[operator]
            if len(unready_taskmanagers) > 0:
                print(f"Warning: at least one taskmanager is not ready: '{unready_taskmanagers}'")

            # Calculate the scale_factor of the ready taskmanagers
            ready_CPU_usages = self.metricsGatherer.gatherCPUUsageOfTaskmanagers(ready_taskmanagers,
                                                                                 taskmanager_cpu_usages)
            if len(ready_CPU_usages) <= 0:
                print(f"Error: list of ready_CPU_usages is empty: 'ready_CPU_usages'. ")
                print(
                    f"Metrics used: read_taskmanagers: '{ready_taskmanagers}', cpu_usages '{taskmanager_cpu_usages}'")
                continue

            ready_average_CPU_value = statistics.mean(ready_CPU_usages)
            currentParallelism = currentParallelisms[operator]

            operator_scale_factor = self.calculateScaleRatio(ready_average_CPU_value,
                                                             self.configurations.CPU_UTILIZATION_TARGET_VALUE)
            desiredParallelism = self.calculateDesiredParallelism(operator_scale_factor, currentParallelism)
            self.addDesiredParallelismForOperator(operator, desiredParallelism)

            # save desired parallelism in list for debug purpose
            desiredParallelisms[operator] = desiredParallelism

        # Get maximum desired parallelisms from scale-down window
        allMaximumDesiredParallelisms: {str, int} = self.getAllMaximumParallelismsFromWindow(self.operators)
        print(f"Desired parallelisms: {desiredParallelisms}")
        print(f"Maximum desired parallelisms: {allMaximumDesiredParallelisms}")
        print(f"Current parallelisms: {currentParallelisms}")
        self.scaleManager.performScaleOperations(currentParallelisms, allMaximumDesiredParallelisms)

