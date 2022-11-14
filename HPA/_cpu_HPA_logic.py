# from HPA_common_logic import getAllDesiredParallelisms
# from gather_metrics import fetchCurrentOperatorParallelismInformation
#
#
# def gatherCPUUtilizationMetrics() -> {str, int}:
#     print("todo")
#     return None
#
# def HPA_UpdateDesiredParallelisms():
#     currentMetrics = gatherCPUUtilizationMetrics()
#     currentParallelisms = fetchCurrentOperatorParallelismInformation(knownOperators=currentMetrics.keys(), v1=v1)
#     desiredParallelisms = getAllDesiredParallelisms(currentMetrics, currentParallelisms, HPA_TARGET_VALUE)
#     for operator in desiredParallelisms.keys():
#         desiredParallelism = desiredParallelisms[operator]
#         addDesiredParallelismForOperator(operator, desiredParallelism)