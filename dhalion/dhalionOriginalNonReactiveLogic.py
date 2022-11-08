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

# Query to run the autoscaler on
QUERY = int(os.environ.get("QUERY", 1))
# Size of the monitoring period
MONITORING_PERIOD_SECONDS = int(os.environ.get("MONITORING_PERIOD_SECONDS", "360"))

# Thresholds
# Scale down factor
SCALE_DOWN_FACTOR = float(os.environ.get("SCALE_DOWN_FACTOR", "0.8"))
# Maximum buffersize for it to be considered 'close to zero'
BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD = float(os.environ.get("BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD", "0.1"))


def getTopology(query):
    """
    Get the topology of the provided query. Supported queries: {1, 3, 11}.
    Topology consists of directed edges from (op1 -> op2).
    :param query: Query to get the topology for
    :return: Topology consisting out of directed edges.
    """
    if query == 1:
        return [
            ("_BidsSource", "Mapper"),
            ("Mapper", "LatencySink"),
        ]
    elif query == 3:
        return [
            ("Source:_auctionsSource", "Incrementaljoin"),
            ("Incrementaljoin", "Sink"),
            ("Source:_personSource", "Filter"),
            ("Filter", "Incrementaljoin")
        ]
    elif query == 11:
        return [
            ("_BidsSource____Timestamps_Watermarks", "SessionWindow____DummyLatencySink")
        ]
    else:
        print(f"ERROR: Unablet to fetch topology from unknown query: '{query}'")
        return []


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


def getAverageBuffersInUsageMetrics() -> {str, float}:
    """
    Fetch average inputBuffer usage of every operator
    :return: A directory with the average input buffer usage of every operator.
    """
    input_usage_average_query = "avg(flink_taskmanager_job_task_buffers_inPoolUsage) by (task_name)"
    input_usage_average_data = getResultsFromPrometheus(input_usage_average_query)
    input_usage_average = extract_per_operator_metrics(input_usage_average_data)
    return input_usage_average


def getMaximumBuffersInUsageMetrics() -> {str, float}:
    """
    Fetch maximum inputBuffer usage of every operator
    :return: A directory with the maximum input buffer usage of every operator.
    """
    input_usage_maximum_query = "max(flink_taskmanager_job_task_buffers_inPoolUsage) by (task_name)"
    input_usage_maximum_data = getResultsFromPrometheus(input_usage_maximum_query)
    input_usage_maximum = extract_per_operator_metrics(input_usage_maximum_data)
    return input_usage_maximum


def getAverageBuffersOutUsageMetrics() -> {str, float}:
    """
    Fetch average outputBuffer usage of every operator
    :return: A directory with the average output buffer usage of every operator.
    """
    output_usage_average_query = "avg(flink_taskmanager_job_task_buffers_outPoolUsage) by (task_name)"
    ouput_usage_average_data = getResultsFromPrometheus(output_usage_average_query)
    output_usage_average = extract_per_operator_metrics(ouput_usage_average_data)
    return output_usage_average


def getMaximumBuffersOutUsageMetrics() -> {str, float}:
    """
    Fetch maximum outputBuffer usage of every operator
    :return: A directory with the maximum output buffer usage of every operator.
    """
    output_usage_maximum_query = "max(flink_taskmanager_job_task_buffers_outPoolUsage) by (task_name)"
    ouput_usage_maximum_data = getResultsFromPrometheus(output_usage_maximum_query)
    output_usage_maximum = extract_per_operator_metrics(ouput_usage_maximum_data)
    return output_usage_maximum


def getBackpressureMetrics() -> {str, bool}:
    """
    Get backpressure metrics from prometheus.
    :return: A direcotry of {operator, boolean} with the boolean indicating whether the operator is backpressured
    """
    backpressure_query = "flink_taskmanager_job_task_isBackPressured"
    backpressure_data = getResultsFromPrometheus(backpressure_query)
    backpressure = extract_per_operator_metrics(backpressure_data)
    results = {}
    for k, v in backpressure.items():
        results[k] = v == 1.0
    return results


def getBackpressuredTimeMetrics() -> {str, float}:
    """
    Get Backpressure time metrics for all operators.
    Backpressure times is the percentage of time the operator was backpressured in the previous MONITORING_PERIOD_SECONDS
    :return: Average backpressure time of flink operator over the monitoring period
    """
    backpressure_time_query = f"avg(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[{MONITORING_PERIOD_SECONDS}s]) / 1000) by (task_name)"
    backpressure_time_data = getResultsFromPrometheus(backpressure_time_query)
    backpressure_time = extract_per_operator_metrics(backpressure_time_data)
    return backpressure_time


def getCurrentParallelismMetrics() -> {str, int}:
    """
    Get the current parallelisms of the individual operators
    :return: A directory with {operator, currentParallelism}
    """
    parallelism_query = "count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)"
    parallelism_data = getResultsFromPrometheus(parallelism_query)
    parallelism = extract_per_operator_metrics(parallelism_data)
    return parallelism


def isBackpressured(backpressure_metrics: {str, bool}) -> bool:
    """
    Check whether one of the operators is experiencing backpressure
    :param backpressure_metrics: A directory with operators as key and backpressure information as values
    :return: Whether at leas tone of the operators is experiencing backpressure.
    """
    return True in backpressure_metrics.values()


def getBottleneckOperators(backpressure_metrics: {str, bool}, topology_edges: [(str, str)]) -> [str]:
    """
    Get all operators that are causing backpressure in the system.
    An operator is said to cause backpressure if it is not experiencing backpressure itself, but at least one of its
    upstream operators is.
    :param backpressure_metrics: Metrics indicating whether operators are experiencing backpressure
    :param topology_edges: The topology of the system, containing directed edges (lop -> rop)
    :return: A list of operators causing backpressure.
    """
    bottleNeckOperatorsSet: set = set()
    for lOperator, rOperator in topology_edges:
        try:
            if backpressure_metrics[lOperator]:
                if not backpressure_metrics[rOperator]:
                    bottleNeckOperatorsSet.add(rOperator)
        except:
            traceback.print_exc()
    return list(bottleNeckOperatorsSet)


def getAllOperators(topology_edges: [(str, str)]):
    """
    Get all existing operators from topology
    :param topology_edges: A topology containing edges between the operators
    :return: A list of operators
    """
    allOperators: set = set()
    for l, r in topology_edges:
        allOperators.add(l)
        allOperators.add(r)
    return list(allOperators)


def queueSizeisCloseToZero(operator: str, inputQueueMetrics: {str, float}, inputQueueThreshold: float):
    """
    Check whether the queuesize of operator {operator} is close to zero.
    This is done by taking the inputQueue size of the operator and check whether it is smaller than inputQueueThreshold
    :param operator: Operator to check the queueSize for
    :param inputQueueMetrics: Directory of inputQueueMetrics with OperatorName as key and its inputQueueSize as value
    :param inputQueueThreshold: Threshold of which the inputQueuesize should be smaller to be close to zero
    :return: Whether the operator's input Queuesize is close to zero
    """
    if operator in inputQueueMetrics.keys():
        if inputQueueMetrics[operator] <= inputQueueThreshold:
            return True
    return False


def getScaleUpFactor(operator: str, backpressureTimeMetrics: {str, float}, topology: (str, str)) -> float:
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
                        f"Error: {operator} from ({op1}, {op2}) not found in backpressure metrics: {backpressureTimeMetrics}")
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


def getDesiredParallelism(operator: str, currentParallelisms: {str, int}, scaling_factor: float, scaling_up: bool):
    """
    Get the desired parallelsim of an operator based on its current parallelism, a scaling facotr and whether it is
    scaling up or down.
    :param operator: Operator to determine the desired parallelism for.
    :param currentParallelisms: The current parallelism of the operator
    :param scaling_factor: The scaling factor to scale by (multiplier).
    :param scaling_up: Whether to scale up or down. Scaling down rounds down, scaling up rounds up.
    :return: The desired parallelisms of the operator
    """
    if operator in currentParallelisms.keys():
        parallelism = currentParallelisms[operator]
        if scaling_up:
            return math.ceil(parallelism * scaling_factor)
        else:
            return math.floor(parallelism * scaling_factor)
    else:
        print(f"Error: {operator} not found in parallelism: {currentParallelisms}")
        return -1


def performScaleOperation(operator: str, desiredParallelism):
    """
    TODO: implement operator-based scaling
    Perform a scaling operator for the operator.
    The desiredParallelism is set between [MIN_TASKMANAGERS, MAX_PARALLELISM]
    :param operator: Operator to scale
    :param desiredParallelism: Operator to scale to.
    :return: None
    """
    desiredParallelism = max(MIN_TASKMANAGERS, desiredParallelism)
    desiredParallelism = min(MAX_TASKMANAGERS, desiredParallelism)
    desired_parallelism[operator] = desiredParallelism
    print(f"Scaling operator '{operator}' to parallelism '{desiredParallelism}'.")


# Value to maintain the current desired values, used for keeping track of operator-specific parallelisms when using
# Flink Reactive.
desired_parallelism = getCurrentParallelismMetrics()


def runSingleDhalionIteration():
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
    time.sleep(MONITORING_PERIOD_SECONDS)

    # Get topology of current query
    topology = getTopology(QUERY)
    # Get Backpressure information of every operator
    backpressureMetrics = getBackpressureMetrics()
    # If backpressure exist, assume unhealthy state and investigate scale up possibilities
    if isBackpressured(backpressureMetrics):
        print("Backpressure detected. System is in a unhealthy state. Investigating scale-up possibilities.")
        # Get operators causing backpressure
        bottleneckOperators: [str] = getBottleneckOperators(backpressureMetrics, topology)
        print(f"The following operators are found to cause a possible bottleneck: {bottleneckOperators}")

        backpressureTimes: {str, float} = getBackpressuredTimeMetrics()
        currentParallelisms: {str, int} = getCurrentParallelismMetrics()
        # For every operator causing backpressure
        for operator in bottleneckOperators:
            # Calculate scale up factor
            operatorScaleUpFactor = getScaleUpFactor(operator, backpressureTimes, topology)
            # Get desired parallelism
            operatorDesiredParallelism = getDesiredParallelism(operator, currentParallelisms, operatorScaleUpFactor,
                                                               True)
            # Scale up the operator
            print(f"{operator}: {operatorScaleUpFactor}, {operatorDesiredParallelism}")

            performScaleOperation(operator, operatorDesiredParallelism)
    # If no backpressure exists, assume a healthy state
    else:
        print("No backpressure detected, system is in an healthy state. Investigating scale-down possibilities.")
        # Get information about input buffers of operators
        buffersInUsage = getMaximumBuffersInUsageMetrics()
        currentParallelisms: {str, int} = getCurrentParallelismMetrics()
        print(buffersInUsage)
        # For every operator
        for operator in getAllOperators(topology):
            # Check if input queue buffer is almost empty
            if queueSizeisCloseToZero(operator, buffersInUsage, BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD):
                # Scale down with SCALE_DOWN_FACTOR
                # Get desired parallelism
                operatorDesiredParallelism = getDesiredParallelism(operator, currentParallelisms, SCALE_DOWN_FACTOR,
                                                                   False)
                # Scale down the operator if using operator-based scaling
                performScaleOperation(operator, operatorDesiredParallelism)


def run_original_dhalion_autoscaler():
    """
    Run Dhalion with operator based scaling scaling.
    :return: None
    """
    while True:
        try:
            runSingleDhalionIteration()
            print(f"Current desired parallelisms: {desired_parallelism}")
            print(f"Current parallelism:          {getCurrentParallelismMetrics()}")
        except:
            traceback.print_exc()
            run_original_dhalion_autoscaler()


def run_original_dhalion_autoscaler_reactive():
    """
    Run Dhalion with Flink Reactive.
    :return: None
    """
    config.load_incluster_config()
    v1_client = client.AppsV1Api()

    def adaptFlinkReactiveTaskmanagers(new_number_of_taskmanagers):
        body = {"spec": {"replicas": new_number_of_taskmanagers}}
        api_response = v1_client.patch_namespaced_deployment_scale(
            name="flink-taskmanager",
            namespace="default",
            body=body,
            pretty=True
        )

    while True:
        try:
            runSingleDhalionIteration()
            max_current_parallelism = max(getCurrentParallelismMetrics())
            max_desired_parallelism = max(desired_parallelism.values())
            if max_current_parallelism != max_desired_parallelism:
                adaptFlinkReactiveTaskmanagers(max_desired_parallelism)
        except:
            traceback.print_exc()
            run_original_dhalion_autoscaler()


if __name__ == "__main__":
    print(f"Running Dhalion Autoscaler with the following configurations: \n"
          f"\tUSE_FLINK_REACTIVE : {USE_FLINK_REACTIVE}\n"
          f"\tPROMETHEUS_SERVER: {PROMETHEUS_SERVER}\n"
          f"\tMIN_TASKMANAGERS: {MIN_TASKMANAGERS}\n"
          f"\tMAX_TASKMANAGERS: {MAX_TASKMANAGERS}\n"
          f"\tQUERY: {QUERY}\n"
          f"\tMONITORING_PERIOD_SECONDS: {MONITORING_PERIOD_SECONDS}\n"
          f"\tSCALE_DOWN_FACTOR: {SCALE_DOWN_FACTOR}\n"
          f"\tBUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD: {BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD}"
          )
    if USE_FLINK_REACTIVE:
        run_original_dhalion_autoscaler_reactive()
    else:
        run_original_dhalion_autoscaler()
