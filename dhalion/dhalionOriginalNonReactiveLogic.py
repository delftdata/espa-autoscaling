import time
import requests

prometheus_server = "34.90.81.123:9090"

def getResultsFromPrometheus(query):
    url = f"http://{prometheus_server}/api/v1/query?query={query}"
    return requests.get(url)

def extract_per_operator_metrics(metrics_json, include_subtask=False):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        if include_subtask:
            metrics_per_operator[operator["metric"]["operator_name"] + " " + operator["metric"]["subtask_index"]] = float(
                operator["value"][1])
        else:
            metrics_per_operator[operator["metric"]["operator_name"]] = float(operator["value"][1])
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

def getBackpressureMetrics():
    backpressure_query = "flink_taskmanager_job_task_isBackPressured"
    backpressure_data = getResultsFromPrometheus(backpressure_query)
    backpressure = extract_per_operator_metrics(backpressure_data)
    return backpressure


def isBackpressured(backpressure_metrics) -> bool:
    return False

def getBottleneckOperators(backpressure_metrics) -> [str]:
    return []





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
    backpressureMetrics = getBackpressureMetrics()
    print(backpressureMetrics)
    print(isBackpressured(backpressureMetrics))
    print(getBottleneckOperators(backpressureMetrics))


    # operators: [str]  = []
    # while True:
    #     # Gather metrics
    #     time.sleep(300)
    #     if isBackpressured():
    #         # Unhealthy state. Detect underprovisioning
    #         bottleneckOperators: [str] = getBottleneckOperators()
    #         for operator in bottleneckOperators:
    #             scaleUpFactor = getScaleUpFactor()
    #             scaleOperator(operator, scaleUpFactor)
    #     else:
    #         for operator in operators:
    #             maximumLag : int = getMaximumOperatorLag(operator)
    #             if lagIsCloseToZero(maximumLag)
    #                 scaleOperator(operator, scaleDownFactor)


def keep_running():
    try:
        run()
    except:
        time.sleep(10)
        keep_running()


keep_running()

