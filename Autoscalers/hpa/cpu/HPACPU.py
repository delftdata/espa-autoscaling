import statistics
import traceback
import time

from HPAConfigurationsCPU import HPAConfigurationsCPU
from HPAMetricsGathererCPU import HPAMetricsGathererCPU
from common import HPALogic
from common import ScaleManager

from kubernetes import client, config


def HPA_CPU_Run(configurations: HPAConfigurationsCPU):
    """
    Run HPA autoscaler.
    It first instantiates all helper classes using the provided configurations.
    Then, it initiates a never-ending loop that catches errors during the iteration and restarts the iteration.
    :param configurations: Configurations class containing all autoscaler configurations
    :return: None
    """
    metricsGatherer: HPAMetricsGathererCPU = HPAMetricsGathererCPU(configurations)
    scaleManager: ScaleManager = ScaleManager(configurations)
    hpa: HPALogic = HPALogic(configurations)

    if configurations.USE_FLINK_REACTIVE:
        config.load_incluster_config()
        v1 = client.AppsV1Api()
        metricsGatherer.v1 = v1
        scaleManager.v1 = v1

    operators = metricsGatherer.jobmanagerMetricGatherer.getOperators()

    def HPA_CPU_Iteration():
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
        time.sleep(configurations.HPA_SYNC_PERIOD_SECONDS)

        # Gather metrics:

        operator_ready_taskmanagers, operator_unready_taskmanagers = metricsGatherer.\
            gatherReady_UnReadyTaskmanagerMapping()
        taskmanager_cpu_usages = metricsGatherer.prometheusMetricGatherer.getTaskmanagerJVMCPUUSAGE()
        currentParallelisms = metricsGatherer.fetchCurrentOperatorParallelismInformation(knownOperators=operators)

        # Per operator, calculate desired parallelism.
        desiredParallelisms = {}  # save desired parallelisms for debug purposes
        for operator in operators:

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
            ready_CPU_usages = metricsGatherer.gatherCPUUsageOfTaskmanagers(ready_taskmanagers, taskmanager_cpu_usages)
            if len(ready_CPU_usages) <= 0:
                print(f"Error: list of ready_CPU_usages is empty: 'ready_CPU_usages'. ")
                print(f"Metrics used: read_taskmanagers: '{ready_taskmanagers}', cpu_usages '{taskmanager_cpu_usages}'")
                continue

            ready_average_CPU_value = statistics.mean(ready_CPU_usages)
            currentParallelism = currentParallelisms[operator]

            operator_scale_factor = hpa.calculateScaleRatio(ready_average_CPU_value,
                                                            configurations.CPU_UTILIZATION_TARGET_VALUE)
            desiredParallelism = hpa.calculateDesiredParallelism(operator_scale_factor, currentParallelism)
            hpa.addDesiredParallelismForOperator(operator, desiredParallelism)

            # save desired parallelism in list for debug purpose
            desiredParallelisms[operator] = desiredParallelism

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


    print("HPA-CPU initialization succeeded. Starting autoscaler loop.")
    while True:
        try:
            HPA_CPU_Iteration()
        except:
            traceback.print_exc()


if __name__ == "__main__":
    print(f"Running HPA-CPU Autoscaler with the following configurations:")
    configs: HPAConfigurationsCPU = HPAConfigurationsCPU()
    configs.printConfigurations()
    for i in range(1, configs.MAX_INITIALIZATION_TRIES+1):
        try:
            HPA_CPU_Run(configs)
        except:
            print(f"Initialization of HPA-CPU failed ({i}/{configs.MAX_INITIALIZATION_TRIES}).")
            traceback.print_exc()
            time.sleep(10)
    print("Maximum amount of initialization tries exceeded. Shutting down autoscaler.")
