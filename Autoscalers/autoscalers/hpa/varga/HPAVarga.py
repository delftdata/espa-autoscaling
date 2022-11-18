import traceback
import time
from abc import ABC

from HPAConfigurationsVarga import HPAConfigurationsVarga
from HPAMetricsGathererVarga import HPAMetricsGathererVarga
from hpa import HPA
from common import ScaleManager
from kubernetes import client, config


class HPAVarga(HPA, ABC):
    configurations: HPAConfigurationsVarga
    metricsGatherer: HPAMetricsGathererVarga
    scaleManager: ScaleManager
    operators: [str]

    def __init__(self):
        self.configurations = HPAConfigurationsVarga()
        self.metricsGatherer: HPAMetricsGathererVarga = HPAMetricsGathererVarga(self.configurations)
        self.scaleManager: ScaleManager = ScaleManager(self.configurations)
        self.operators = self.metricsGatherer.jobmanagerMetricGatherer.getOperators()

        if self.configurations.USE_FLINK_REACTIVE:
            config.load_incluster_config()
            v1 = client.AppsV1Api()
            self.metricsGatherer.v1 = v1
            self.scaleManager.v1 = v1

    def runHPAVargaIteration(self):
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
        time.sleep(self.configurations.HPA_SYNC_PERIOD_SECONDS)

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
        allMaximumDesiredParallelisms: {str, int} = self.getAllMaximumParallelismsFromWindow(operators)
        print(f"Desired parallelisms: {desiredParallelisms}")
        print(f"Maximum desired parallelisms: {allMaximumDesiredParallelisms}")
        print(f"Current parallelisms: {currentParallelisms}")
        self.scaleManager.performScaleOperations(
            currentParallelisms,
            allMaximumDesiredParallelisms,
            cooldownPeriod=self.configurations.COOLDOWN_PERIOD_SECONDS
        )

    def run(self):
        """
        Run HPA autoscaler.
        It first instantiates all helper classes using the provided configurations.
        Then, it initiates a never-ending loop that catches errors during the iteration and restarts the iteration.
        :return: None
        """
        print("Varga initialization succeeded. Starting autoscaler loop.")
        while True:
            try:
                self.runHPAVargaIteration()
            except:
                traceback.print_exc()
