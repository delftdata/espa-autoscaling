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
        avg_cpu_usages: float = metricsGatherer.gatherAvgCPUUsagePerOperator()
        currentParallelisms = metricsGatherer.fetchCurrentOperatorParallelismInformation(knownOperators=operators)

        # Calculate desired parallelisms based on metrics
        desiredParallelisms = hpa.calculateAllDesiredParallelisms(
            avg_cpu_usages,
            currentParallelisms,
            configurations.HPA_TARGET_VALUE
        )

        # Add desired parallelisms to scale-down window
        if len(desiredParallelisms) != len(operators):
            print(f"Warning: desired parallelisms '{desiredParallelisms}' does not contain all operators '{operators}.")
        for operator in desiredParallelisms.keys():
            hpa.addDesiredParallelismForOperator(operator,  desiredParallelisms[operator])

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
    configs.printConfigurations()
    for i in range(1, configs.HPA_MAX_INITIALIZATION_TRIES+1):
        try:
            HPA_Run(configs)
        except:
            print(f"Initialization of HPA failed ({i}/{configs.HPA_MAX_INITIALIZATION_TRIES}).")
            traceback.print_exc()
            time.sleep(10)
    print("Maximum amount of initialization tries exceeded. Shutting down autoscaler.")
