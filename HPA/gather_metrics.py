import math
import time
import requests
import traceback
from kubernetes import client, config
import os

# IMPORTANT: Do not use " " when providing environmental variables. It will not work with this script.

# Whether to use Flink Reactive for scaling operators
USE_FLINK_REACTIVE = os.environ.get("USE_FLINK_REACTIVE", "False").lower() in ["true", "1", "t"]
# Address of the prometheus server
PROMETHEUS_SERVER = os.environ.get("PROMETHEUS_SERVER", "prometheus-server")

# Minimum amount of taskmanagers
MIN_TASKMANAGERS = int(os.environ.get("MIN_TASKMANAGERS", 1))
# Maximum amount of taskmanagers
MAX_TASKMANAGERS = int(os.environ.get("MAX_TASKMANAGERS", 16))


def getResultsFromPrometheus(query):
    """
    Get the results of a query from Prometheus.
    Prometheus should be fetched from PROMETHEUS_SERVER
    :param query: Query to fetch results for from Prometheus
    :return: A response object send by the Prometheus server.
    """
    url = f"http://{PROMETHEUS_SERVER}/api/v1/query?query={query}"
    return requests.get(url)


def extract_per_operator_metrics(prometheusResponse):
    """
    Extract per-operator- metrics from the prometheusResponse
    :param prometheusResponse: Response received from Prometheus containing query results
    :return: A directory with per-operator values {operator: values}
    """
    metrics = prometheusResponse.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
    return metrics_per_operator


def getCurrentParallelismMetrics() -> {str, int}:
    """
    Get the current parallelisms of the individual operators
    :return: A directory with {operator, currentParallelism}
    """
    parallelism_query = f"count(sum_over_time(flink_taskmanager_job_task_operator_numRecordsIn[{METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
    parallelism_data = getResultsFromPrometheus(parallelism_query)
    parallelism = extract_per_operator_metrics(parallelism_data)
    return parallelism


def getCurrentNumberOfTaskmanagersMetrics(v1) -> int:
    try:
        number_of_taskmanagers = -1
        ret = v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True,
                                            field_selector="metadata.name=flink-taskmanager")
        for i in ret.items:
            number_of_taskmanagers = int(i.spec.replicas)
        return number_of_taskmanagers
    except:
        traceback.print_exc()
        return -1



def gatherUtilizationMetrics() -> {str, int}:
    print("todo")
    return None

def gatherRelativeLagChangeMetrics() -> {str, int}:
    print("todo")
    return None

def fetchCurrentOperatorParallelismInformation(knownOperators: [str] = None, v1=None) -> {str, int}:
    """
    Get per-operator parallelism
    If Flink reactive is used:
        Fetch current amount of taskmanagers
        Return a direcotry with all operators having this parallelism
        v1 is required for this scenario
    If Flink reactive is not used:
        Fetch taskmanagers using the getCurrentParallelismMetrics() function.
        v1 is not required for this scenario
    :param v1: Only required when using Flink Reactive. Used to fetch current amount of taskmanagers
    :return: Directory with operators as key and parallelisms as values
    """
    if USE_FLINK_REACTIVE:
        if not v1:
            print(f"Error: no valid configurations of v1: {v1}")
            return {}

        currentTaskmanagers = getCurrentNumberOfTaskmanagersMetrics(v1)
        if currentTaskmanagers < 0:
            print(f"Error: no valid amount of taskmanagers found: {currentTaskmanagers}")
            return {}

        operatorParallelismInformation = {}
        for operator in knownOperators:
            operatorParallelismInformation[operator] = currentTaskmanagers
        return operatorParallelismInformation
    else:
        return getCurrentParallelismMetrics()





