import statistics
import traceback
import time

from common import Configurations
from common import HPALogic
from common import MetricsGatherer
from common import ScaleManager

from kubernetes import client, config


def HPA_Run(configurations: Configurations):
    """
    Run HPA autoscaler.
    It first instantiates all helper classes using the provided configurations.
    Then, it initiates a never-ending loop that catches errors during the iteration and restarts the iteration.
    :param configurations: Configurations class containing all autoscaler configurations
    :return: None
    """
    metricsGatherer: MetricsGatherer = MetricsGatherer(configurations)
    scaleManager: ScaleManager = ScaleManager(configurations)
    hpa: HPALogic = HPALogic(configurations)

    if configurations.USE_FLINK_REACTIVE:
        config.load_incluster_config()
        v1 = client.AppsV1Api()
        metricsGatherer.v1 = v1
        scaleManager.v1 = v1

    operators = metricsGatherer.jobmanagerMetricGatherer.getOperators()

    def HPA_Iteration():
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

        print("\nStarting next HPA iteration.")
        time.sleep(configurations.HPA_SYNC_PERIOD_SECONDS)

        # Gather metrics:

        operator_ready_taskmanagers, operator_unready_taskmanagers = metricsGatherer.gatherReady_UnReadyTaskmanagerMapping()
        taskmanager_cpu_usages = metricsGatherer.prometheusMetricGatherer.getTaskmanagerJVMCPUUSAGE()
        currentParallelisms = metricsGatherer.fetchCurrentOperatorParallelismInformation(knownOperators=operators)

        # Per operator, calculate desired parallelism.
        desiredParallelisms = {}  # save desired parallelisms for debug purposes
        for operator in operators:

            # Check if all metrics are available for operator
            if operator not in operator_ready_taskmanagers:
                print(f"Error: operator '{operator}' not found in operator_ready_taskmanagers '{operator_ready_taskmanagers}'")
                continue
            if operator not in operator_unready_taskmanagers:
                print(f"Error: operator '{operator}' not found in operator_unready_taskmanagers '{operator_unready_taskmanagers}'")
                continue
            if operator not in currentParallelisms:
                print(f"Error: operator '{operator}' not found in current parallelisms '{currentParallelisms}'")
                continue

            ready_taskmanagers = operator_ready_taskmanagers[operator]
            unready_taskmanagers = operator_unready_taskmanagers[operator]

            # Calculate the scale_factor of the ready taskmanagers
            ready_CPU_usages = metricsGatherer.gatherCPUUsageOfTaskmanagers(ready_taskmanagers, taskmanager_cpu_usages)
            if len(ready_CPU_usages) <= 0:
                print(f"Error: list of ready_CPU_usages is empty: 'ready_CPU_usages'. ")
                print(f"Metrics used: read_taskmanagers: '{ready_taskmanagers}', cpu_usages '{taskmanager_cpu_usages}'")
                continue

            ready_average_CPU_value = statistics.mean(ready_CPU_usages)
            ready_scale_factor = hpa.calculateScaleRatio(ready_average_CPU_value, configurations.HPA_TARGET_VALUE)
            operator_scale_factor = ready_scale_factor

            print(f"Ready taskmanagers {ready_taskmanagers}, operator_scale_factor = {operator_scale_factor}")

            # If we have unready taskmanagers, calculate scale_factor of them
            if len(unready_taskmanagers) > 0:
                print("Checking whether scale_factor still holds when taking unready taskmanagers into consideration")

                assumed_metric = 1 if ready_scale_factor < 1 else 0
                all_CPU_usages = ready_CPU_usages + [assumed_metric for _ in unready_taskmanagers]
                if len(all_CPU_usages) <= 0:
                    print(f"Error: list of all_CPU_usages is empty: '{all_CPU_usages}'. ")
                    print(
                        f"Metrics used: unready_taskmanagers: '{unready_taskmanagers}', all_CPU_usages '{all_CPU_usages}'")
                    continue

                all_average_CPU_value = statistics.mean(all_CPU_usages)
                all_ready_scale_factor = hpa.calculateScaleRatio(all_average_CPU_value, configurations.HPA_TARGET_VALUE)
                print(f"Unready taskmanagers {unready_taskmanagers}, scalefactor: {all_ready_scale_factor}")

                if (all_ready_scale_factor < 1 and ready_scale_factor < 1) \
                        or (all_ready_scale_factor > 1 and ready_scale_factor > 1):
                    operator_scale_factor = all_ready_scale_factor
                else:
                    operator_scale_factor = 1

            print(f"operator_scale_factor: {operator_scale_factor}")

            currentParallelism = currentParallelisms[operator]
            desiredParallelism = hpa.calculateDesiredParallelism(operator_scale_factor, currentParallelism)
            hpa.addDesiredParallelismForOperator(operator, desiredParallelism)

            desiredParallelisms[operator] = desiredParallelism # save desired parallelism for debug purpose

        # Get maximum desired parallelisms from scale-down window
        allMaximumDesiredParallelisms: {str, int} = hpa.getAllMaximumParallelismsFromWindow(operators)

        print(f"Desired parallelisms: {desiredParallelisms}")
        print(f"Maximum desired parallelisms: {allMaximumDesiredParallelisms}")
        print(f"Current parallelisms: {currentParallelisms}")

        # Scale if current parallelism is different than desired parallelism
        if configurations.USE_FLINK_REACTIVE:
            desiredTaskmanagersAmount = max(allMaximumDesiredParallelisms.values())
            currentTaskmanagerAmount = max(currentParallelisms.values())
            if currentTaskmanagerAmount != desiredTaskmanagersAmount:
                scaleManager.adaptFlinkReactiveTaskmanagers(desiredTaskmanagersAmount)
        else:
            for operator in allMaximumDesiredParallelisms:
                currentParallelism = currentParallelisms[operator]
                desiredParallelism = allMaximumDesiredParallelisms[operator]
                if currentParallelism != desiredParallelism:
                    scaleManager.scaleOperator(operator, desiredParallelism)


    print("HPA initialization succeeded. Starting autoscaler loop.")
    while True:
        try:
            HPA_Iteration()
        except:
            traceback.print_exc()


if __name__ == "__main__":
    print(f"Running HPA Autoscaler with the following configurations:")
    configs: Configurations = Configurations()
    configs.PROMETHEUS_SERVER = "34.91.177.156:9090"
    configs.FLINK_JOBMANAGER_SERVER = "35.204.189.88:8081"
    configs.SCALE_DOWN_WINDOW_SECONDS = 30
    configs.USE_FLINK_REACTIVE = False
    configs.printConfigurations()
    for i in range(1, configs.HPA_MAX_INITIALIZATION_TRIES+1):
        try:
            HPA_Run(configs)
        except:
            print(f"Initialization of HPA failed ({i}/{configs.HPA_MAX_INITIALIZATION_TRIES}).")
            traceback.print_exc()
            time.sleep(10)
    print("Maximum amount of initialization tries exceeded. Shutting down autoscaler.")
