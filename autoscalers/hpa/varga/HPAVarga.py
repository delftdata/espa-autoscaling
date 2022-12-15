import time
from abc import ABC

from .HPAVargaConfigurations import HPAVargaConfigurations
from .HPAVargaApplicationManager import HPAVargaApplicationManager
from hpa.HPA import HPA
from common import ScaleManager


class HPAVarga(HPA, ABC):
    configurations: HPAVargaConfigurations
    metricsGatherer: HPAVargaApplicationManager
    scaleManager: ScaleManager
    operators: [str]

    def __init__(self):
        self.configurations = HPAVargaConfigurations()
        self.metricsGatherer: HPAVargaApplicationManager = HPAVargaApplicationManager(self.configurations)
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

        print("\nStarting next HPA-Varga iteration.")
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Gather metrics:
        currentParallelisms = self.metricsGatherer.fetchCurrentOperatorParallelismInformation(
            knownOperators=self.operators)
        operatorUtilizationMetrics = self.metricsGatherer.gatherUtilizationMetrics()
        operatorRelativeLagChangeMetrics = self.metricsGatherer.gatherRelativeLagChangeMetrics()

        # Calculate desired parallelism per operator
        desiredParallelisms = {}  # save desired parallelisms for debug purposes
        for operator in self.operators:
            if operator not in operatorUtilizationMetrics:
                print(f"Error: operator '{operator}' not found in utilizatonMetrics '{operatorUtilizationMetrics}'")
                continue
            if operator not in operatorRelativeLagChangeMetrics:
                print(f"Error: operator '{operator}' not found in relativeLagChangeMetrics "
                      f"'{operatorRelativeLagChangeMetrics}'")
                continue

            currentParallelism = currentParallelisms[operator]

            utilization = operatorUtilizationMetrics[operator]
            utilization_scale_factor = self.calculateScaleRatio(utilization,
                                                                self.configurations.VARGA_UTILIZATION_TARGET_VALUE)

            relativeLagChange = operatorRelativeLagChangeMetrics[operator]
            relativeLagChange_scale_factor = self.calculateScaleRatio(
                relativeLagChange, self.configurations.VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE)

            # Determine desired parallelism and add to scale-down-window
            operator_scale_factor = max(utilization_scale_factor, relativeLagChange_scale_factor)
            desiredParallelism = self.calculateDesiredParallelism(operator_scale_factor, currentParallelism)
            self.addDesiredParallelismForOperator(operator, desiredParallelism)

            # save desired parallelism in list for debug purpose
            desiredParallelisms[operator] = desiredParallelism

        # Manage scaling actions

        # Get maximum desired parallelisms from scale-down window
        allMaximumDesiredParallelisms: {str, int} = self.getAllMaximumParallelismsFromWindow(self.operators)
        print(f"Desired parallelisms: {desiredParallelisms}")
        print(f"Maximum desired parallelisms: {allMaximumDesiredParallelisms}")
        print(f"Current parallelisms: {currentParallelisms}")
        self.scaleManager.performScaleOperations(currentParallelisms, allMaximumDesiredParallelisms)
