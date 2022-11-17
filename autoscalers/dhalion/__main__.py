import time
import traceback
from kubernetes import client, config

from common import ScaleManager
from DhalionMetricsGatherer import DhalionMetricsGatherer
from DhalionLogic import DhalionLogic
from DhalionConfigurations import DhalionConfigurations


def Dhalion_Run(configurations: DhalionConfigurations):
    """
    Run Dhalion autoscaler.
    It first instantiates all helper classes using the provided configurations.
    Then, it initiates a never-ending loop that catches errors during the iteration and restarts the iteration.
    :param configurations: Configurations class containing all autoscaler configurations
    :return: None
    """
    metricsGatherer: DhalionMetricsGatherer = DhalionMetricsGatherer(configurations)
    scaleManager: ScaleManager = ScaleManager(configurations)
    dhalion: DhalionLogic = DhalionLogic(configurations)

    if configurations.USE_FLINK_REACTIVE:
        config.load_incluster_config()
        v1 = client.AppsV1Api()
        metricsGatherer.v1 = v1
        scaleManager.v1 = v1

    operators = metricsGatherer.jobmanagerMetricGatherer.getOperators()
    topology = metricsGatherer.jobmanagerMetricGatherer.getTopology()

    def Dhalion_Iteration():
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
        time.sleep(configurations.DHALION_MONITORING_PERIOD_SECONDS)

        # Get Backpressure information of every operator
        backpressureStatusMetrics = metricsGatherer.gatherBackpressureStatusMetrics()
        currentParallelisms: {str, int} = metricsGatherer.fetchCurrentOperatorParallelismInformation(
            knownOperators=operators
        )

        # If backpressure exist, assume unhealthy state and investigate scale up possibilities
        if metricsGatherer.isSystemBackpressured(backpressureStatusMetrics=backpressureStatusMetrics):
            print("Backpressure detected. System is in a unhealthy state. Investigating scale-up possibilities.")

            # Get operators causing backpressure
            bottleneckOperators: [str] = metricsGatherer.gatherBottleneckOperators(
                backpressureStatusMetrics=backpressureStatusMetrics,
                topology=topology
            )
            print(f"The following operators are found to cause a possible bottleneck: {bottleneckOperators}")


            backpressureTimeMetrics: {str, float} = metricsGatherer.gatherBackpressureTimeMetrics(
                monitoringPeriodSeconds=configurations.DHALION_MONITORING_PERIOD_SECONDS)

            print(f"Found the following metrics are found:")
            print(f"\tBackpressure-times[{backpressureTimeMetrics}]")
            print(f"\tcurrentParallelisms[{currentParallelisms}]")

            # For every operator causing backpressure
            for operator in bottleneckOperators:
                # Calculate scale up factor
                operatorScaleUpFactor = dhalion.calculateScaleUpFactor(operator, backpressureTimeMetrics, topology)
                # Get desired parallelism
                operatorDesiredParallelism = dhalion.calculateDesiredParallelism(
                    operator,
                    currentParallelisms,
                    operatorScaleUpFactor
                )
                # Save desired parallelism
                dhalion.setDesiredParallelism(operator, operatorDesiredParallelism)

        # If no backpressure exists, assume a healthy state
        else:
            print("No backpressure detected, system is in an healthy state. Investigating scale-down possibilities.")
            # Get information about input buffers of operators
            buffersInUsage = metricsGatherer.gatherBuffersInUsageMetrics()

            print(f"Found the following metrics are found:")
            print(f"\tBuffer-in-usage[{buffersInUsage}]")
            print(f"\tcurrentParallelisms[{currentParallelisms}]")

            # For every operator
            for operator in operators:
                # Check if input queue buffer is almost empty
                if dhalion.queueSizeisCloseToZero(operator, buffersInUsage,
                                                  configurations.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD):
                    # Scale down with SCALE_DOWN_FACTOR
                    # Get desired parallelism
                    operatorDesiredParallelism = dhalion.calculateDesiredParallelism(
                        operator,
                        currentParallelisms,
                        configurations.DHALION_SCALE_DOWN_FACTOR
                    )

                    # Scale down the operator if using operator-based scaling
                    dhalion.calculateDesiredParallelism(operator, operatorDesiredParallelism)

            # Manage scaling actions
            desiredParallelisms = dhalion.getDesiredParallelisms()
            print(f"Desired parallelisms: {desiredParallelisms}")
            print(f"Current parallelisms: {currentParallelisms}")
            scaleManager.performScaleOperations(
                currentParallelisms,
                desiredParallelisms,
                cooldownPeriod=configurations.COOLDOWN_PERIOD_SECONDS
            )

        print("Dhalion initialization succeeded. Starting autoscaler loop.")
        while True:
            try:
                Dhalion_Iteration()
            except:
                traceback.print_exc()


if __name__ == "__main__":
    print(f"Running Dhalion Autoscaler with the following configurations:")
    configs: DhalionConfigurations = DhalionConfigurations()
    configs.printConfigurations()
    for i in range(1, configs.MAX_INITIALIZATION_TRIES):
        try:
            Dhalion_Run(configs)
        except:
            print(f"Initialization of HPA failed ({i}/{configs.MAX_INITIALIZATION_TRIES}).")
            traceback.print_exc()
            time.sleep(10)
    print("Maximum amount of initialization tries exceeded. Shutting down autoscaler.")
