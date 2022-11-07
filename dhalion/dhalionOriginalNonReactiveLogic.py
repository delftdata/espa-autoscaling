import math
import time
import requests
import traceback
from kubernetes import client, config

PROMETHEUS_SERVER = "35.204.17.221:9090"


MAX_TASKMANAGERS = 16
MIN_TASKMANAGERS = 1
QUERY = 3
SCALE_DOWN_FACTOR = 0.8
BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD = 0.1
MONITORING_PERIOD_SECONDS = 10


topology_q1 = [
    ("_BidsSource", "Mapper"),
    ("Mapper", "LatencySink"),
]


topology_q3 = [
    ("Source:_auctionsSource", "Incrementaljoin"),
    ("Incrementaljoin", "Sink"),
    ("Source:_personSource", "Filter"),
    ("Filter", "Incrementaljoin")
]

topology_q11 = [
    ("_BidsSource____Timestamps_Watermarks", "SessionWindow____DummyLatencySink")
]

def getTopology(query):
    if query == 1:
        return topology_q1
    elif query == 3:
        return topology_q3
    elif query == 11:
        return topology_q11
    else:
        print(f"ERROR: Unablet to fetch topology from unknown query: '{query}'")
        return []


def getResultsFromPrometheus(query):
    url = f"http://{PROMETHEUS_SERVER}/api/v1/query?query={query}"
    return requests.get(url)


def extract_per_operator_metrics(metrics_json, include_subtask=False):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        if include_subtask:
            metrics_per_operator[operator["metric"]["task_name"] + " " + operator["metric"]["subtask_index"]] = float(
                operator["value"][1])
        else:
            metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
    return metrics_per_operator




def getAverageBuffersInUsageMetrics() -> {str, float}:
    input_usage_average_query = "avg(flink_taskmanager_job_task_buffers_inPoolUsage) by (task_name)"
    input_usage_average_data = getResultsFromPrometheus(input_usage_average_query)
    input_usage_average = extract_per_operator_metrics(input_usage_average_data)
    return input_usage_average


def getMaximumBuffersInUsageMetrics() -> {str, float}:
    input_usage_maximum_query = "max(flink_taskmanager_job_task_buffers_inPoolUsage) by (task_name)"
    input_usage_maximum_data = getResultsFromPrometheus(input_usage_maximum_query)
    input_usage_maximum = extract_per_operator_metrics(input_usage_maximum_data)
    return input_usage_maximum


def getAverageBuffersOutUsageMetrics() -> {str, float}:
    output_usage_average_query = "avg(flink_taskmanager_job_task_buffers_outPoolUsage) by (task_name)"
    ouput_usage_average_data = getResultsFromPrometheus(output_usage_average_query)
    output_usage_average = extract_per_operator_metrics(ouput_usage_average_data)
    return output_usage_average


def getMaximumBuffersOutUsageMetrics() -> {str, float}:
    output_usage_maximum_query = "max(flink_taskmanager_job_task_buffers_outPoolUsage) by (task_name)"
    ouput_usage_maximum_data = getResultsFromPrometheus(output_usage_maximum_query)
    output_usage_maximum = extract_per_operator_metrics(ouput_usage_maximum_data)
    return output_usage_maximum


def getBackpressureMetrics() -> {str, float}:
    backpressure_query = "flink_taskmanager_job_task_isBackPressured"
    backpressure_data = getResultsFromPrometheus(backpressure_query)
    backpressure = extract_per_operator_metrics(backpressure_data)
    results = {}
    for k, v in backpressure.items():
        results[k] = v == 1.0
    return results

def getBackpressuredTimeMetrics() -> {str, float}:
    backpressure_time_query = f"avg(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[{MONITORING_PERIOD_SECONDS}s]) / 1000) by (task_name)"
    backpressure_time_data = getResultsFromPrometheus(backpressure_time_query)
    backpressure_time = extract_per_operator_metrics(backpressure_time_data)
    return backpressure_time

def getCurrentParallelismMetrics() -> {str, int}:
    parallelism_query = "count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)"
    parallelism_data = getResultsFromPrometheus(parallelism_query)
    parallelism = extract_per_operator_metrics(parallelism_data)
    return parallelism


def isBackpressured(backpressure_metrics: {str, bool}) -> bool:
    return True in backpressure_metrics.values()


def getBottleneckOperators(backpressure_metrics: {str, bool}, topology_edges: [(str, str)]) -> [str]:
    bottleNeckOperatorsSet : set = set()
    for lOperator, rOperator in topology_edges:
        try:
            if backpressure_metrics[lOperator]:
                if not backpressure_metrics[rOperator]:
                    bottleNeckOperatorsSet.add(rOperator)
        except:
            traceback.print_exc()
    return list(bottleNeckOperatorsSet)



def getAllOperators(topology_edges: [(str, str)]):
    allOperators: set = set()
    for l, r in topology_edges:
        allOperators.add(l)
        allOperators.add(r)
    return list(allOperators)



def queueSizeisCloseToZero(operator: str, inputQueueMetrics: {str, float}, inputQueueFloat: float):
    if operator in inputQueueMetrics.keys():
        if inputQueueMetrics[operator] <= inputQueueFloat:
            return True
    return False


def getScaleUpFactor(operator: str, backpressureTimes: {str, float}) -> float:
    """
    ScaleupFactor is calculated using the following formula:
    "Percentage of time that the Heron Instance spent suspending the input data over the amount of time where
    backpressure was not observed"
    """
    if operator in backpressureTimes.keys():
        backpressureTime = backpressureTimes[operator]
        normalTime = 1 - backpressureTime
        return 1 + backpressureTime / normalTime
    else:
        print(f"Error: {operator} not found in backpressure metrics: {backpressureTimes}")
        return 1


def getDesiredParallelism(operator: str, currentParallelisms: {str, int}, scaling_factor: float):
    if operator in currentParallelisms.keys():
        parallelism = currentParallelisms[operator]
        newParallelism = math.ceil(parallelism * scaling_factor)
        return newParallelism
    else:
        print(f"Error: {operator} not found in parallelism: {currentParallelisms}")
        return -1


def performScaleOperation(operator: str, desiredParallelism):
    desiredParallelsim = max(MIN_TASKMANAGERS, desiredParallelism)
    desiredParallelsim = min(MAX_TASKMANAGERS, desiredParallelism)
    DESIRED_PARALELISMS[operator] = desiredParallelism
    print(f"Scaling operator {operator} to {desiredParallelism}")


config.load_incluster_config()
v1 = client.AppsV1Api()
def scaleTaskmanagers(desiredTaskmanagerParallelism):
    print("Scaling taskmanagers")
    body = {"spec": {"replicas": desiredTaskmanagerParallelism}}
    api_response = v1.patch_namespaced_deployment_scale(
        name="flink-taskmanager", namespace="default", body=body,
        pretty=True)

def runSingleDhalionIteration():
    time.sleep(MONITORING_PERIOD_SECONDS)
    """
    If backpressure exists:
        If backpressure cannot be contributed to slow instances or skew (it can't:
            Find bottleneck causing the backpressure
            Scale up bottleneck
    else if no backpressure exists:
        if for all instances of operator, the average number of pending packets is almost 0:
            scale down with {underprovisioning system}
    if after scaling down, backpressure is observed:
        undo action and blacklist action
    """
    # Get topology of current query
    topology = getTopology(QUERY)
    # Get Backpressure information of every operator
    backpressureMetrics = getBackpressureMetrics()
    # If backpressure exist, assume unhealthy state and investigate scale up possibilities
    if isBackpressured(backpressureMetrics):
        # Get operators causing backpressure
        bottleneckOperators: [str] = getBottleneckOperators(backpressureMetrics, topology)

        backpressureTimes: {str, float} = getBackpressuredTimeMetrics()
        currentParallelisms: {str, int} = getCurrentParallelismMetrics()
        # For every operator causing backpressure
        for operator in bottleneckOperators:
            # Calculate scale up factor
            operatorScaleUpFactor = getScaleUpFactor(operator, backpressureTimes)
            # Get desired parallelism
            operatorDesiredParallelism = getDesiredParallelism(operator, currentParallelisms, operatorScaleUpFactor)
            # Scale up the operator
            performScaleOperation(operator, operatorDesiredParallelism)
    # If no backpressure exists, assume a healthy state
    else:
        # Get information about input buffers of operators
        buffersInUsage = getMaximumBuffersInUsageMetrics()
        currentParallelisms: {str, int} = getCurrentParallelismMetrics()
        # For every operator
        for operator in getAllOperators(topology):
            # Check if input queue buffer is almost empty
            if queueSizeisCloseToZero(operator, buffersInUsage, BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD):
                # Scale down with SCALE_DOWN_FACTOR
                # Get desired parallelism
                operatorDesiredParallelism = getDesiredParallelism(operator, currentParallelisms, SCALE_DOWN_FACTOR)
                # Scale down the operator
                performScaleOperation(operator, operatorDesiredParallelism)

    # Perform Reactive operation
    if max(getCurrentParallelismMetrics().values()) != max(DESIRED_PARALELISMS):
        scaleTaskmanagers(max(DESIRED_PARALELISMS))



DESIRED_PARALELISMS = getCurrentParallelismMetrics()
def run_original_dhalion_autoscaler():
    while True:
        try:
            runSingleDhalionIteration()
            print(f"Current desired parallelisms: {DESIRED_PARALELISMS}")
        except:
            traceback.print_exc()
            run_original_dhalion_autoscaler()


if __name__ == "__main__":
    run_original_dhalion_autoscaler()

