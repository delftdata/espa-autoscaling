import math
import time
from abc import ABC, abstractmethod

from .HPAConfigurations import HPAConfigurations
from common import Autoscaler


class HPA(Autoscaler, ABC):
    configurations: HPAConfigurations

    """
    A director containing all desired parallelisms.
    Structure.
    - Key = operator name
    - Value = (float, int)
        - p0: time desired parallelism was added
        - p1: desired parallelism
    """
    desiredParallelisms = {}

    def addDesiredParallelismForOperator(self, operator: str, desiredParallelism: int):
        """
        Add desired parallelism to desiredParallelisms list
        :param operator: operator to add parallelism too
        :param desiredParallelism: desired parallelism of operator
        :return: None
        """
        if operator not in self.desiredParallelisms.keys():
            self.desiredParallelisms[operator] = []
        self.desiredParallelisms[operator].append((time.time(), desiredParallelism))

    def __updateScaleDownWindow(self):
        """
        Update desiredParallelisms based on the scale-down operator
        :return:
        """
        for operator in self.desiredParallelisms.keys():
            parallelisms = self.desiredParallelisms[operator]
            updated_parallelisms = list(filter(
                lambda v: time.time() - v[0] <= self.configurations.HPA_SCALE_DOWN_WINDOW_SECONDS,
                parallelisms
            ))
            self.desiredParallelisms[operator] = updated_parallelisms

    def getKnownOperators(self):
        """
        Get a list of all operators we know of
        :return: List of all known operators
        """
        return self.desiredParallelisms.keys()

    def __getMaximumParallelismOfOperatorFromWindow(self, operator):
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
                print(f"Error: failed fetching max parallelism of operator {operator}: no desired parallelisms found")
                return -1
        else:
            print(f"Error: failed fetching maximum parallelism of operator {operator}: operator unknown")
            return -1


    def getAllMaximumParallelismsFromWindow(self, operators: [str]) -> {str, int}:
        self.__updateScaleDownWindow()
        allMaximumParallelisms: {str, int} = {}
        for operator in operators:
            allMaximumParallelisms[operator] = self.__getMaximumParallelismOfOperatorFromWindow(operator)
        return allMaximumParallelisms


    def calculateScaleRatio(self, current_metric_variable: float, target_metric_variable: float):
        """
        Calcualte the scale ratio based on the current_metric_variable and the target_metric_variable
        :param current_metric_variable: Current metric variable
        :param target_metric_variable: Target metric variable
        :return: Scale factor calculated by current_metric_variable / target_metric_variable
        """
        scaleRatio = current_metric_variable / target_metric_variable
        return scaleRatio


    def calculateDesiredParallelism(self, scale_factor: float, current_parallelism):
        """
        Based on the scale_factor and the current_parallelism. Determine the desired parallelism.
        The desired_parallelism should be in range between (MIN_PARALLELISM and MAX_PARALLELISM)
        :param scale_factor: scale_factor to scale operator by
        :param current_parallelism: current parallelism of operator
        :return: desired parallelism of operator
        """
        new_desired_parallelism = math.ceil(current_parallelism * scale_factor)
        new_desired_parallelism = min(new_desired_parallelism, self.configurations.MAX_PARALLELISM)
        new_desired_parallelism = max(new_desired_parallelism, self.configurations.MIN_PARALLELISM)
        return new_desired_parallelism

    @abstractmethod
    def runAutoscalerIteration(self):
        pass

    @abstractmethod
    def setInitialMetrics(self):
        pass
