import math
from DhalionConfigurations import DhalionConfigurations

class DhalionLogic:

    desiredParallelisms: {str, int}
    configurations: DhalionConfigurations

    def __init__(self, configurations: DhalionConfigurations, currentParallelisms: {str, int}):
        self.configurations = configurations
        self.desiredParallelisms = currentParallelisms

    def setDesiredParallelism(self, operator: str, desiredParallelism: int):
        self.desiredParallelisms[operator] = desiredParallelism

    def getDesiredParallelisms(self) -> {str, int}:
        return self.desiredParallelisms


    def queueSizeisCloseToZero(self, operator: str, inputQueueMetrics: {str, float}):
        """
        Check whether the queuesize of operator {operator} is close to zero.
        This is done by taking the inputQueue size of the operator and check whether it is smaller than
        inputQueueThreshold
        :param operator: Operator to check the queueSize for
        :param inputQueueMetrics: Directory of inputQueueMetrics with OperatorName as key and its inputQueueSize as
        value
        :param inputQueueThreshold: Threshold of which the inputQueuesize should be smaller to be close to zero
        :return: Whether the operator's input Queuesize is close to zero
        """
        if operator in inputQueueMetrics.keys():
            if inputQueueMetrics[operator] <= self.configurations.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD:
                return True
        return False


    @staticmethod
    def calculateScaleUpFactor(operator: str, backpressureTimeMetrics: {str, float}, topology: (str, str))\
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
            print(backpressureValues)
            backpressureTime = 0
            if backpressureValues is not None:
                backpressureTime = max(backpressureValues)
            else:
                print(f"Warning: no backpressure cause found for {operator}")
            normalTime = 1 - backpressureTime
            scaleUpFactor = 1 + backpressureTime / normalTime
            return scaleUpFactor
        else:
            print(f"Error: {operator} not found in backpressure metrics: {backpressureTimeMetrics}")
            return 1

    def calculateDesiredParallelism(self, operator: str, currentParallelisms: {str, int}, scaling_factor: float):
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
            desiredParallelism = min(desiredParallelism, self.configurations.MAX_PARALLELISM)
            desiredParallelism = max(desiredParallelism, self.configurations.MIN_PARALLELISM)
            return desiredParallelism
        else:
            print(f"Error: {operator} not found in parallelism: {currentParallelisms}")
            return -1
