import time
import requests
import traceback

prometheus_server = "34.90.34.128:9090"


# topology_q1 = [
#     ("_BidsSource", "Mapper"),
#     ("Mapper", "LatencySink"),
# ]


topology_q3 = [
    ("Source:_auctionsSource", "Incrementaljoin"),
    ("Incrementaljoin", "Sink"),
    ("Source:_personSource", "Filter"),
    ("Filter", "Incrementaljoin")
]

# topology_q11 = [
#     ("_BidsSource____Timestamps_Watermarks", "SessionWindow____DummyLatencySink")
# ]

def getResultsFromPrometheus(query):
    url = f"http://{prometheus_server}/api/v1/query?query={query}"
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


def getBackpressureMetrics() -> {str, float}:
    backpressure_query = "flink_taskmanager_job_task_isBackPressured"
    backpressure_data = getResultsFromPrometheus(backpressure_query)
    backpressure = extract_per_operator_metrics(backpressure_data)
    results = {}
    for k, v in backpressure.items():
        results[k] = v == 1.0
    return results


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




def getScaleUpFactor() -> int:
    """
    ScaleupFactor is calculated using the following formula:
         percentage of time instances spend suspending input tata
        / amount of time backpressure was not observed
    :return:
    """
    pass


def getMaximumOperatorLag(operator: str):
    pass


def scaleOperator(operator: str, scale_factor: float):
    pass

def lagIsCloseToZero(lag: int):
    pass

scaleDownFactor = 0.8
overprovisioningLagThreshold = 100000


def run():
    topology = topology_q3
    while True:
        # Gather metrics
        time.sleep(300)

        backpressureMetrics = getBackpressureMetrics()

        if isBackpressured(backpressureMetrics):
            # Unhealthy state. Underprovisioning detection

            # Fetch all operators that are recognized as bottlenecks
            bottleneckOperators: [str] = getBottleneckOperators(backpressureMetrics, topology)
            for operator in bottleneckOperators:
                # TODO: Calculate scale-up factor of operators
                scaleUpFactor = getScaleUpFactor()
                # TODO: Scale operator
                scaleOperator(operator, scaleUpFactor)

        else:
            for operator in getAllOperators(topology):
                maximumLag : int = getMaximumOperatorLag(operator)
                if lagIsCloseToZero(maximumLag)
                    scaleOperator(operator, scaleDownFactor)


def keep_running():
    while True:
        try:
            run()
            time.sleep(10)
        except:
            traceback.print_exc()
            time.sleep(10)
            keep_running()


if __name__ == "__main__":
    keep_running()

