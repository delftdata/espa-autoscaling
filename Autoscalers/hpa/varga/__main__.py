import traceback
import time

from HPAConfigurationsVarga import HPAConfigurationsVarga
from HPAMetricsGathererVarga import HPAMetricsGathererVarga
from hpa import HPALogic
from common import ScaleManager
from kubernetes import client, config


def HPA_Varga_Run(configurations: HPAConfigurationsVarga):
    """
    Run HPA autoscaler.
    It first instantiates all helper classes using the provided configurations.
    Then, it initiates a never-ending loop that catches errors during the iteration and restarts the iteration.
    :param configurations: Configurations class containing all autoscaler configurations
    :return: None
    """
    metricsGatherer: HPAMetricsGathererVarga = HPAMetricsGathererVarga(configurations)
    scaleManager: ScaleManager = ScaleManager(configurations)
    hpa: HPALogic = HPALogic(configurations)

    if configurations.USE_FLINK_REACTIVE:
        config.load_incluster_config()
        v1 = client.AppsV1Api()
        metricsGatherer.v1 = v1
        scaleManager.v1 = v1

    operators = metricsGatherer.jobmanagerMetricGatherer.getOperators()

    def HPA_Varga_Iteration():
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
        time.sleep(configurations.HPA_SYNC_PERIOD_SECONDS)

        # Gather metrics:
        currentParallelisms = metricsGatherer.fetchCurrentOperatorParallelismInformation(knownOperators=operators)
        operatorUtilizationMetrics = metricsGatherer.gatherUtilizationMetrics()
        operatorRelativeLagChangeMetrics = metricsGatherer.gatherRelativeLagChangeMetrics()

        # Calculate desired parallelism per operator
        desiredParallelisms = {}  # save desired parallelisms for debug purposes
        for operator in operators:
            if operator not in operatorUtilizationMetrics:
                print(f"Error: operator '{operator}' not found in utilizatonMetrics '{operatorUtilizationMetrics}'")
                continue
            if operator not in operatorRelativeLagChangeMetrics:
                print(f"Error: operator '{operator}' not found in relativeLagChangeMetrics "
                      f"'{operatorRelativeLagChangeMetrics}'")
                continue

            currentParallelism = currentParallelisms[operator]

            utilization = operatorUtilizationMetrics[operator]
            utilization_scale_factor = hpa.calculateScaleRatio(utilization,
                                                               configurations.VARGA_UTILIZATION_TARGET_VALUE)

            relativeLagChange = operatorRelativeLagChangeMetrics[operator]
            relativeLagChange_scale_factor = hpa.calculateScaleRatio(
                relativeLagChange, configurations.VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE)

            # Determine desired parallelism and add to scale-down-window
            operator_scale_factor = max(utilization_scale_factor, relativeLagChange_scale_factor)
            desiredParallelism = hpa.calculateDesiredParallelism(operator_scale_factor, currentParallelism)
            hpa.addDesiredParallelismForOperator(operator, desiredParallelism)

            # save desired parallelism in list for debug purpose
            desiredParallelisms[operator] = desiredParallelism

        # Manage scaling actions

        # Get maximum desired parallelisms from scale-down window
        allMaximumDesiredParallelisms: {str, int} = hpa.getAllMaximumParallelismsFromWindow(operators)
        print(f"Desired parallelisms: {desiredParallelisms}")
        print(f"Maximum desired parallelisms: {allMaximumDesiredParallelisms}")
        print(f"Current parallelisms: {currentParallelisms}")
        scaleManager.performScaleOperations(
            currentParallelisms,
            allMaximumDesiredParallelisms,
            cooldownPeriod=configurations.COOLDOWN_PERIOD_SECONDS
        )

    print("Varga initialization succeeded. Starting autoscaler loop.")
    while True:
        try:
            HPA_Varga_Iteration()
        except:
            traceback.print_exc()


if __name__ == "__main__":
    print(f"Running HPA-Varga Autoscaler with the following configurations:")
    configs: HPAConfigurationsVarga = HPAConfigurationsVarga()
    configs.printConfigurations()
    for i in range(1, configs.MAX_INITIALIZATION_TRIES+1):
        try:
            HPA_Varga_Run(configs)
        except:
            print(f"Initialization of HPA-Varga failed ({i}/{configs.MAX_INITIALIZATION_TRIES}).")
            traceback.print_exc()
            time.sleep(10)
    print("Maximum amount of initialization tries exceeded. Shutting down autoscaler.")
