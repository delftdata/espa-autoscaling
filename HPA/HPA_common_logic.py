import time
import os
import math

from gather_metrics import gatherCPUUtilizationMetrics, fetchCurrentOperatorParallelismInformation

ITERATION_SLEEP_TIME_SECONDS = int(os.environ.get("ITERATION_SLEEP_TIME_SECONDS", 5))
SCALE_DOWN_WINDOW_SECONDS = int(os.environ.get("SCALE_DOWN_WINDOW_SECONDS", 25))

MAX_PARALLELISM = int(os.environ.get("MAX_PARALLELISM", 1))
MIN_PARALLELISM = int(os.environ.get("MIN_PARALLELISM", 1))

HPA_TARGET_VALUE = float(os.environ.get("HPA_MAX_TARGET_VALUE"))
#
# def performScaleOperation(operator: str, desiredParallelism):
#     """
#     TODO: implement operator-based scaling
#     Perform a scaling operator for the operator.
#     The desiredParallelism is set between [MIN_TASKMANAGERS, MAX_PARALLELISM]
#     :param operator: Operator to scale
#     :param desiredParallelism: Operator to scale to.
#     :return: None
#     """
#     desiredParallelism = max(MIN_TASKMANAGERS, desiredParallelism)
#     desiredParallelism = min(MAX_TASKMANAGERS, desiredParallelism)
#     desired_parallelism[operator] = desiredParallelism
#     print(f"Scaling operator '{operator}' to parallelism '{desiredParallelism}'.")
#

"""
A director containing all desired parallelisms.
Structure.
- Key = operator name
- Value = (float, int)
    - p0: time desired parallelism was added
    - p1: desired parallelism
"""
desiredParallelisms = {}


def addDesiredarallelism(operator: str, desiredParallelism: int):
    """
    Add desired parallelism to desiredParallelisms list
    :param operator: operator to add parallelism too
    :param desiredParallelism: desired parallelism of operator
    :return: None
    """
    if not operator in desiredParallelisms.keys():
        desiredParallelisms[operator] = []
    desiredParallelisms[operator].append((time.time(), desiredParallelism))


def updateScaleDownWindow():
    """
    Update desiredParallelisms based on the scale-down operator
    :return:
    """
    for operator in desiredParallelisms.keys():
        parallelisms = desiredParallelisms[operator]
        updated_parallelisms = list(filter(lambda v: time.time() - v[0] <= SCALE_DOWN_WINDOW_SECONDS, parallelisms))
        desiredParallelisms[operator] = updated_parallelisms


def getKnownOperators():
    """
    Get a list of all operators we know of
    :return: List of all known operators
    """
    return desiredParallelisms.keys()


def getMaximumParallelism(operator):
    """
    Get the maximum parallelism for operator {operator}
    :param operator: Operator to get maximum parallelism for
    :return: Parallelism or operator. -1 if invalid parameters.
    """
    if operator in desiredParallelisms.keys():
        parallelisms = list(map(lambda t: t[1], desiredParallelisms[operator]))
        if len(parallelisms) > 0:
            return max(parallelisms)
        else:
            print(f"Error: failed fetching maximum parallelism of operator {operator}: no desired parallelisms found")
            return -1
    else:
        print(f"Error: failed fetching maximum parallelism of operator {operator}: operator unknown")
        return -1


def getDesiredParallelism(current_metric_variable: float, target_metric_variable: float, current_parallelism):
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
    new_desired_parallelism = min(new_desired_parallelism, MAX_PARALLELISM)
    new_desired_parallelism = max(new_desired_parallelism, MIN_PARALLELISM)
    return new_desired_parallelism

def getAllDesiredParallelisms(operatorMetrics: {str, float}, current_parallelisms: {str, float}, targetValue):
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
            desiredParallelism = getDesiredParallelism(operatorMetrics[], targetValue)
            desiredParallelisms[operator] = desiredParallelism
        else:
            print(f"Error: did not find parallelism of operator {operator}  in {current_parallelisms}")
    return desiredParallelisms



def varga_UpdateDesiredParallelisms():
    currentUtilizationmetrics =

def singleHPAIteration(v1 = None):
    time.sleep(ITERATION_SLEEP_TIME_SECONDS)
    gatherUtilizationMetrics()

    c



if __name__ == "__main__":
    for i in range(0, 100):
        addDesiredarallelism("test1", i % 6)
        updateScaleDownWindow()
        for operator in getKnownOperators():
            print(f"Maximum parallelism of operator '{operator}': {getMaximumParallelism(operator)}")