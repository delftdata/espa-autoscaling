

from Configurations import Configurations
from MetricsGatherer import MetricGatherer
from HPA import HPA



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
#
# def varga_UpdateDesiredParallelisms():
#     currentUtilizationmetrics =
#
# # def singleHPAIteration(v1 = None):
# #     time.sleep(ITERATION_SLEEP_TIME_SECONDS)
# #     gatherUtilizationMetrics()
# #
# #     c


if __name__ == "__main__":
    configs = Configurations()
    configs.PROMETHEUS_SERVER = "34.91.91.253:9090"
    configs.FLINK_JOBMANAGER_SERVER = "34.91.68.163:8081"
    gatherer = MetricGatherer(configs)
    print(gatherer.jobTopologyData_getTopology())
