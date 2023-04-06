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
    desired_parallelisms = {}

    def add_desired_parallelism_for_operator(self, operator: str, desired_parallelism: int) -> None:
        """
        Add desired parallelism to desiredParallelisms list
        :param operator: operator to add parallelism too
        :param desired_parallelism: desired parallelism of operator
        :return: None
        """
        if operator not in self.desired_parallelisms.keys():
            self.desired_parallelisms[operator] = []
        self.desired_parallelisms[operator].append((time.time(), desired_parallelism))

    def __update_scale_down_window(self) -> None:
        """
        Update desiredParallelisms based on the scale-down operator
        :return: None
        """
        for operator in self.desired_parallelisms.keys():
            parallelisms = self.desired_parallelisms[operator]
            updated_parallelisms = list(filter(
                lambda v: time.time() - v[0] <= self.configurations.HPA_SCALE_DOWN_WINDOW_SECONDS,
                parallelisms
            ))
            self.desired_parallelisms[operator] = updated_parallelisms

    def get_known_operators(self) -> [str]:
        """
        Get a list of all operators we know of
        :return: List of all known operators
        """
        return self.desired_parallelisms.keys()

    def __get_maximum_parallelism_of_operator_from_window(self, operator) -> int:
        """
        Get the maximum parallelism for operator {operator}
        :param operator: Operator to get maximum parallelism for
        :return: Parallelism or operator. -1 if invalid parameters.
        """
        if operator in self.desired_parallelisms.keys():
            parallelisms = list(map(lambda t: t[1], self.desired_parallelisms[operator]))
            if len(parallelisms) > 0:
                return max(parallelisms)
            else:
                print(f"Error: failed fetching maximum parallelism of operator {operator}: no desired parallelisms found")
                return -1
        else:
            print(f"Error: failed fetching maximum parallelism of operator {operator}: operator unknown")
            return -1


    def get_all_maximum_parallelisms_from_window(self, operators: [str]) -> dict[str, int]:
        self.__update_scale_down_window()
        all_maximum_parallelisms: {str, int} = {}
        for operator in operators:
            all_maximum_parallelisms[operator] = self.__get_maximum_parallelism_of_operator_from_window(operator)
        return all_maximum_parallelisms

    @staticmethod
    def calculate_scale_ratio(current_metric_variable: float, target_metric_variable: float) -> float:
        """
        Calcualte the scale ratio based on the current_metric_variable and the target_metric_variable
        :param current_metric_variable: Current metric variable
        :param target_metric_variable: Target metric variable
        :return: Scale factor calculated by current_metric_variable / target_metric_variable
        """
        scale_ratio = current_metric_variable / target_metric_variable
        return scale_ratio

    @staticmethod
    def calculate_desired_parallelism(scale_factor: float, current_parallelism) -> int:
        """
        Based on the scale_factor and the current_parallelism. Determine the desired parallelism.
        The desired_parallelism should be in range between (MIN_PARALLELISM and MAX_PARALLELISM)
        :param scale_factor: scale_factor to scale operator by
        :param current_parallelism: current parallelism of operator
        :return: desired parallelism of operator
        """
        new_desired_parallelism = math.ceil(current_parallelism * scale_factor)
        new_desired_parallelism = max(new_desired_parallelism, 1)
        return new_desired_parallelism

    @abstractmethod
    def run_autoscaler_iteration(self):
        pass
