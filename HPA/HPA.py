import math
import time
from Configurations import Configurations


class HPA:
    configurations: Configurations

    """
    A director containing all desired parallelisms.
    Structure.
    - Key = operator name
    - Value = (float, int)
        - p0: time desired parallelism was added
        - p1: desired parallelism
    """
    desiredParallelisms = {}

    def __init__(self, configurations: Configurations):
        self.configurations = configurations

    def addDesiredParallelismForOperator(self, operator: str, desiredParallelism: int):
        """
        Add desired parallelism to desiredParallelisms list
        :param operator: operator to add parallelism too
        :param desiredParallelism: desired parallelism of operator
        :return: None
        """
        if not operator in self.desiredParallelisms.keys():
            self.desiredParallelisms[operator] = []
        self.desiredParallelisms[operator].append((time.time(), desiredParallelism))

    def updateScaleDownWindow(self):
        """
        Update desiredParallelisms based on the scale-down operator
        :return:
        """
        for operator in self.desiredParallelisms.keys():
            parallelisms = self.desiredParallelisms[operator]
            updated_parallelisms = list(filter(lambda v: time.time() - v[0] <= self.configurations.SCALE_DOWN_WINDOW_SECONDS, parallelisms))
            self.desiredParallelisms[operator] = updated_parallelisms

    def getKnownOperators(self):
        """
        Get a list of all operators we know of
        :return: List of all known operators
        """
        return self.desiredParallelisms.keys()

    def getMaximumParallelismOfOperator(self, operator):
        """
        Get the maximum parallelism for operator {operator}
        :param operator: Operator to get maximum parallelism for
        :return: Parallelism or operator. -1 if invalid parameters.
        """
        if operator in self.desiredParallelisms.keys():
            parallelisms = list(map(lambda t: t[1], self.desiredParallelisms[operator]))
            if len(parallelisms) > 0:
                return max(parallelisms)
            else:
                print(f"Error: failed fetching maximum parallelism of operator {operator}: no desired parallelisms found")
                return -1
        else:
            print(f"Error: failed fetching maximum parallelism of operator {operator}: operator unknown")
            return -1

    def __calculateDesiredParallelism(self, current_metric_variable: float, target_metric_variable: float, current_parallelism):
        """
        Given a current metric value, the target metric value and the current parallelism.
        Calculate the desired parallelism.
        Desired parallelism is set between MAX_PARALLELISM and MIN_PARALLELISM
        :param current_metric_variable: Current metric value
        :param target_metric_variable: Target metric value
        :param current_parallelism: Current parallelism of operator
        :return: Desired parallelism of operator
        """
        multiplier: float = current_metric_variable / target_metric_variable
        new_desired_parallelism = math.ceil(current_parallelism * multiplier)
        new_desired_parallelism = min(new_desired_parallelism, self.configurations.MAX_PARALLELISM)
        new_desired_parallelism = max(new_desired_parallelism, self.configurations.MIN_PARALLELISM)
        return new_desired_parallelism

    def calculateAllDesiredParallelisms(self, operatorMetrics: {str, float}, current_parallelisms: {str, float}, targetValue):
        """
        Given all operatorMetrics, currentParallelisms and targetvalue, calculate for all autoscalers the desired
        parallelism.
        :param operatorMetrics: Current metrics per operator. Directory with {operatorName, current Metric}
        :param current_parallelisms: Current parallelisms per operator. Direcotry with {operatorName, current Metric}
        :param targetValue:
        :return:
        """
        desiredParallelisms = {}
        for operator in operatorMetrics.keys():
            if operator in current_parallelisms.keys():
                desiredParallelism = self.__calculateDesiredParallelism(operatorMetrics, targetValue)
                desiredParallelisms[operator] = desiredParallelism
            else:
                print(f"Error: did not find parallelism of operator {operator}  in {current_parallelisms}")
        return desiredParallelisms

