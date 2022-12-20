import math
from abc import ABC
import time

from .DhalionConfigurations import DhalionConfigurations
from .DhalionApplicationManager import DhalionApplicationManager

from common import ScaleManager
from common import Autoscaler


class Dhalion(Autoscaler, ABC):

    desiredParallelisms: {str, int}
    configurations: DhalionConfigurations
    applicationManager: DhalionApplicationManager
    scaleManager: ScaleManager
    operators: [str]
    topology: [(str, str)]


    def __init__(self):
        self.configurations = DhalionConfigurations()
        self.applicationManager = DhalionApplicationManager(self.configurations)
        self.scaleManager: ScaleManager = ScaleManager(self.configurations, self.applicationManager)

    def initialize(self):
        self.applicationManager.initialize()
        self.operators = self.applicationManager.jobmanagerManager.getOperators()
        self.topology = self.applicationManager.gatherTopology(False)
        print(f"Found operators: '{self.operators}' with topology: '{self.topology}'")
        currentParallelism = self.applicationManager.fetchCurrentOperatorParallelismInformation(
            knownOperators=self.operators
        )
        print(f"Found initial parallelisms: '{currentParallelism}'")
        self.desiredParallelisms = currentParallelism


    def setDesiredParallelism(self, operator: str, desiredParallelism: int):
        self.desiredParallelisms[operator] = desiredParallelism

    def getDesiredParallelisms(self) -> {str, int}:
        return self.desiredParallelisms


    def queueSizeIsCloseToZero(self, operator: str, inputQueueMetrics: {str, float}):
        """
        Check whether the queuesize of operator {operator} is close to zero.
        This is done by taking the inputQueue size of the operator and check whether it is smaller than
        inputQueueThreshold
        :param operator: Operator to check the queueSize for
        :param inputQueueMetrics: Directory of inputQueueMetrics with OperatorName as key and its inputQueueSize as
        value
        :return: Whether the operator's input Queuesize is close to zero
        """
        if operator in inputQueueMetrics.keys():
            if inputQueueMetrics[operator] <= self.configurations.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD:
                return True
        return False


    def calculateScaleUpFactor(self, operator: str, backpressureTimeMetrics: {str, float}, topology: (str, str))\
            -> float:
        """
        Calculate the scaleUpFactor for operator {operator}.
        The calculations are based on the backpressureTimeMetrics and the current topology.
        ScaleUp factor is calculated in the following way:
        - Get backpressuretimes of all upstream operators of {operator}
        - Pick maximum backpressuretime as backpressureTime
        - scaleUpFactor = 1 + (backpressureTime / (1 - backpressureTime)
        :param operator: Operator to calculate scale-up factor for
        :param backpressureTimeMetrics: A directory of backpressuretimes with operator names as keys.
        :param topology: Topology of the current query. Should contain a list of directed edges.
        :return: ScaleUpFactor
        """
        if not self.configurations.experimentData.operatorIsASource(operator):
            print(f"Calculating scale factor of regular operator: {operator}")
            if operator in backpressureTimeMetrics.keys():
                backpressureValues = []
                for op1, op2 in topology:
                    if op2 == operator:
                        if op1 in backpressureTimeMetrics.keys():
                            backpressureValues.append(backpressureTimeMetrics[op1])
                        else:
                            print(
                                f"Error: {operator} from ({op1}, {op2}) not found in backpressure metrics: "
                                f"{backpressureTimeMetrics}")
                backpressureTime = 0
                if backpressureValues is not None:
                    backpressureTime = max(backpressureValues)
                else:
                    print(f"Warning: no backpressure cause found for {operator}")

                backpressureTime = min(0.9, backpressureTime)
                normalTime = 1 - backpressureTime
                scaleUpFactor = 1 + backpressureTime / normalTime

                return scaleUpFactor
            else:
                print(f"Error: {operator} not found in backpressure metrics: {backpressureTimeMetrics}")
                return 1
        else:
            print(f"Calculating scale factor of soucre operator: {operator}")


    @staticmethod
    def calculateDesiredParallelism(operator: str, currentParallelisms: {str, int}, scaling_factor: float):
        """
        Get the desired parallelsim of an operator based on its current parallelism, a scaling facotr and whether it is
        scaling up or down.
        :param operator: Operator to determine the desired parallelism for.
        :param currentParallelisms: The current parallelism of the operator
        :param scaling_factor: The scaling factor to scale by (multiplier).
        :return: The desired parallelisms of the operator
        """
        if operator in currentParallelisms.keys():
            parallelism = currentParallelisms[operator]
            if scaling_factor >= 1:
                desiredParallelism = math.ceil(parallelism * scaling_factor)
            else:
                desiredParallelism = math.floor(parallelism * scaling_factor)
            desiredParallelism = max(desiredParallelism, 1)
            return desiredParallelism
        else:
            print(f"Error: {operator} not found in parallelism: {currentParallelisms}")
            return -1


    def runAutoscalerIteration(self):
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
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Get Backpressure information of every operator

        operatorBackpressureStatusMetrics = self.applicationManager.gatherOperatorBackpressureStatusMetrics()
        sourceOperatorBackpressureStatusMetrics = self.applicationManager\
            .gatherSourceOperatorBackpressureStatusMetrics()
        print(operatorBackpressureStatusMetrics)
        print(sourceOperatorBackpressureStatusMetrics)

        currentParallelisms: {str, int} = self.applicationManager.fetchCurrentOperatorParallelismInformation(
            knownOperators=self.operators
        )

        # If backpressure exist, assume unhealthy state and investigate scale up possibilities
        if self.applicationManager.isSystemBackpressured(
                operatorBackpressureStatusMetrics=operatorBackpressureStatusMetrics,
                sourceOperatorBackpressureStatusMetrics=sourceOperatorBackpressureStatusMetrics):
            print("Backpressure detected. System is in a unhealthy state. Investigating scale-up possibilities.")

            # Get operators causing backpressure
            bottleneckOperators: [str] = self.applicationManager.gatherBottleneckOperators(
                operatorBackpressureStatusMetrics=operatorBackpressureStatusMetrics,
                sourceOperatorBackpressureStatusMetrics=sourceOperatorBackpressureStatusMetrics,
                topology=self.topology
            )
            print(f"The following operators are found to cause a possible bottleneck: {bottleneckOperators}")

            backpressureTimeMetrics: {str, float} = self.applicationManager.gatherBackpressureTimeMetrics(
                monitoringPeriodSeconds=self.configurations.ITERATION_PERIOD_SECONDS)

            print(f"The following metrics are found:")
            print(f"\tBackpressure-times[{backpressureTimeMetrics}]")
            print(f"\tcurrentParallelisms[{currentParallelisms}]")

            # For every operator causing backpressure
            for operator in bottleneckOperators:
                # Calculate scale up factor
                operatorScaleUpFactor = self.calculateScaleUpFactor(operator, backpressureTimeMetrics, self.topology)
                # Get desired parallelism
                operatorDesiredParallelism = self.calculateDesiredParallelism(
                    operator,
                    currentParallelisms,
                    operatorScaleUpFactor
                )
                print(f"Determined a scale-up factor of {operatorScaleUpFactor} for operator {operator}, which resulted"
                      f" in desired parallelism {operatorDesiredParallelism}")

                # Save desired parallelism
                self.setDesiredParallelism(operator, operatorDesiredParallelism)

        # If no backpressure exists, assume a healthy state
        else:
            print(
                "No backpressure detected, system is in an healthy state. Investigating scale-down possibilities.")
            # Get information about input buffers of operators
            buffersInUsage = self.applicationManager.gatherBuffersInUsageMetrics()

            print(f"Found the following metrics are found:")
            print(f"\tBuffer-in-usage[{buffersInUsage}]")
            print(f"\tcurrentParallelisms[{currentParallelisms}]")

            # For every operator
            for operator in self.operators:
                # Check if input queue buffer is almost empty
                if self.queueSizeIsCloseToZero(operator, buffersInUsage):
                    # Scale down with SCALE_DOWN_FACTOR
                    # Get desired parallelism
                    operatorDesiredParallelism = self.calculateDesiredParallelism(
                        operator,
                        currentParallelisms,
                        self.configurations.DHALION_SCALE_DOWN_FACTOR
                    )

                    self.setDesiredParallelism(operator, operatorDesiredParallelism)

        # Manage scaling actions
        desiredParallelisms = self.getDesiredParallelisms()
        print(f"Desired parallelisms: {desiredParallelisms}")
        print(f"Current parallelisms: {currentParallelisms}")
        self.scaleManager.performScaleOperations(currentParallelisms, desiredParallelisms)
