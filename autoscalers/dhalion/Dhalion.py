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
        """
        Initialize Dhalion initializing the remaining application connections and fetching non-changing experiment
        settings.
        """
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
        """
        Set the desired parallelism of operator {operator}
        """
        self.desiredParallelisms[operator] = desiredParallelism

    def getDesiredParallelisms(self) -> {str, int}:
        """
        Get the current desired parallelism.
        """
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
            return inputQueueMetrics[operator] <= self.configurations.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD
        else:
            print(f"Warning: operator '{operator}' not found in inputQueueMetrics {inputQueueMetrics}")
            return False

    def pendingRecordsIsCloseToZero(self, sourceOperator, pendingRecordsMetrics: {str, int}):
        f"""
        Check whether the pending records of sourceOperator {sourceOperator} is close to zero.
        This is done by taking the total amount of pendingRecords and check whether it is smaller than
        DHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD.
        :param sourceOperator: operator to check whether its pendingRecords is close to zero
        :param pendingRecordsMetrics: Directory of sourceOperators and the amount of pending records for this operator
        :return: Whether the kafka lag corresponding to the sourceOperator is close to zero.
        """
        if sourceOperator in pendingRecordsMetrics:
            return pendingRecordsMetrics[sourceOperator] <= self.configurations.DHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD
        else:
            print(f"Warning: sourceOperator '{sourceOperator}' not found in pendingRecordsMetrics "
                  f"{pendingRecordsMetrics}")
            return False

    @staticmethod
    def calculateOperatorScaleUpFactor(operator: str, backpressureTimeMetrics: {str, float}, topology: (str, str))\
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
        print(f"Calculating scale factor of regular operator: {operator}")
        backpressureValues = []
        for op1, op2 in topology:
            if op2 == operator:
                if op1 in backpressureTimeMetrics.keys():
                    backpressureValues.append(backpressureTimeMetrics[op1])
                else:
                    print(
                        f"Error: {operator} from ({op1}, {op2}) not found in backpressure metrics: "
                        f"{backpressureTimeMetrics}")

        if backpressureValues:
            backpressureTime = max(backpressureValues)
        else:
            print(f"Warning: no backpressure values found for victims of slow operator '{operator}'")
            backpressureTime = 0

        # scaleUpFactor is not allowed to be larger than 10 and cannot be smaller than 1
        backpressureTime = min(0.9, backpressureTime)
        normalTime = 1 - backpressureTime
        scaleUpFactor = 1 + backpressureTime / normalTime
        return scaleUpFactor

    @staticmethod
    def calculateSourceOperatorScaleUpFactor(operator, sourceOperatorPendingRecordsRateMetrics,
                                             sourceOperatorConsumedRecordsRateMetrics) -> float:
        """
        Calculate the scale-up factor of a source operator.
        This is done with the following formula:
        Scaleup factor = pending_records_rate / source_input_rate
        The scaleup factor cannot be larger than 10 and cannot be smaller than 1
        """
        print(f"Calculating scale factor of source operator: {operator}")
        if operator in sourceOperatorPendingRecordsRateMetrics and operator in sourceOperatorConsumedRecordsRateMetrics:
            pendingRecordsRate = sourceOperatorPendingRecordsRateMetrics[operator]
            consumedRecordsRate = sourceOperatorConsumedRecordsRateMetrics[operator]
            if consumedRecordsRate != 0:
                scaleUpFactor = 1 + pendingRecordsRate / consumedRecordsRate
            else:
                scaleUpFactor = 10
            # scaleUpFactor is not allowed to be larger than 10 and cannot be smaller than 1
            scaleUpFactor = max(1, min(10, scaleUpFactor))
            return scaleUpFactor
        else:
            print(f"Warning: pending records rate and/or consumed records rate cause found for source operator"
                  f" {operator}")

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
        sourceOperatorBackpressureStatusMetrics = self.applicationManager.gatherSourceOperatorBackpressureStatusMetrics(
            self.configurations.DHALION_KAFKA_LAG_RATE_TO_BE_BACKPRESSURED_THRESHOLD)

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
                operatorBackpressureStatusMetrics, sourceOperatorBackpressureStatusMetrics,self.topology)
            print(f"The following operators are found to cause a possible bottleneck: {bottleneckOperators}")

            # Fetching metrics: operator_backpressure_times, source_pending_record_rates, source_consumed_record_rates
            operatorBackpressureTimeMetrics: {str, float} = self.applicationManager.gatherBackpressureTimeMetrics(
                monitoringPeriodSeconds=self.configurations.ITERATION_PERIOD_SECONDS)
            sourceOperatorPendingRecordsRateMetrics = self.applicationManager.gatherOperatorPendingRecordsRateMetrics()
            sourceOperatorConsumedRecordsRateMetrics = self.applicationManager.gatherOperatorConsumedRecordsRateMetrics()
            print(f"The following metrics are found:")
            print(f"\tBackpressure-times[{operatorBackpressureTimeMetrics}]")
            print(f"\tSource-pending-records-rate[{sourceOperatorPendingRecordsRateMetrics}]")
            print(f"\tSource-consumed-records-rate[{sourceOperatorConsumedRecordsRateMetrics}]")

            # For every operator causing backpressure
            for operator in bottleneckOperators:

                # If operator is a source
                if self.configurations.experimentData.operatorIsASource(operator):
                    # Calculate operatorScaleUpFactor for a source
                    operatorScaleUpFactor = self.calculateSourceOperatorScaleUpFactor(
                        operator, sourceOperatorPendingRecordsRateMetrics, sourceOperatorConsumedRecordsRateMetrics)
                else:
                    # Calculate operatorScaleUpFactor for a regular operator
                    operatorScaleUpFactor = self.calculateOperatorScaleUpFactor(
                        operator, operatorBackpressureTimeMetrics, self.topology)

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
            inputQueueMetrics = self.applicationManager.gatherBuffersInUsageMetrics()
            pendingRecordsMetrics = self.applicationManager.gatherSourceOperatorPendingRecordMetrics()
            print(f"Found the following metrics are found:")
            print(f"\tBuffer-in-usage[{inputQueueMetrics}]")
            print(f"\tPending-records[{pendingRecordsMetrics}]")
            print(f"\tcurrentParallelisms[{currentParallelisms}]")

            # For every operator
            for operator in self.operators:
                # Check if input queue buffer is almost empty
                if self.configurations.experimentData.operatorIsASource(operator):
                    operatorHasNoLag = self.pendingRecordsIsCloseToZero(operator, pendingRecordsMetrics)
                    if operatorHasNoLag:
                        print(f"Source-operator {operator} is not experiencing any lag. Scaling down operator")
                    else:
                        print(f"Source-operator {operator} is experiencing lag. Source-operator is not scaled down.")
                else:
                    operatorHasNoLag = self.queueSizeIsCloseToZero(operator, inputQueueMetrics)
                    if operatorHasNoLag:
                        print(f"Operator {operator} is not experiencing any lag. Scaling down operator")
                    else:
                        print(f"Operator {operator} is experiencing lag. Operator is not scaled down.")

                if operatorHasNoLag:
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
