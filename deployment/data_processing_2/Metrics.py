from enum import Enum


class MetricClass(Enum):
    """
    An Enum class of all available metrics.
    This class can be used as a mapping between the metric and the used MetricName (String)
    """
    INPUT_RATE = "input_rate"
    TASKMANAGER = "taskmanager"
    LATENCY = "latency"
    LAG = "lag"
    THROUGHPUT = "throughput"
    CPU_LOAD = "CPU_load"
    BACKPRESSURE = "backpressure"
    BUSY_TIME = "busy_time"
    IDLE_TIME = "idle_time"


def getAllMetricClasses():
    """
    Get a list of all MetricClasses
    :return: list of all MetricClasses
    """
    return [
        MetricClass.INPUT_RATE,
        MetricClass.TASKMANAGER,
        MetricClass.LATENCY,
        MetricClass.LAG,
        MetricClass.THROUGHPUT,
        MetricClass.CPU_LOAD,
        MetricClass.BACKPRESSURE,
        MetricClass.BUSY_TIME,
        MetricClass.IDLE_TIME
    ]


def getMetricName(metric: MetricClass):
    """
    Get the corresponding metricName (type String) from a MetricClass (type MetricClass)
    :param metric: MetricClass (type MetricClass) to convert to MetricName (type String)
    :return: A MetricName (type String)
    """
    return metric.value


# def getMetricClass(metricName: String):
#     return ((MetricClass) metricName).getName()


def convertMetricClassestoMetricNames(metricClasses: [MetricClass]):
    """
    Convert a list of metrics to a list of MetricNames
    :param metricClasses: a list of metrics (type Metric)
    :return: a list of metricNames (type String)
    """
    return list(map(lambda mc: getMetricName(mc), metricClasses))


def getAllMetricNames():
    """
    Get a list of all metricNames (type String)
    :return: a list of all metricNames (type String)
    """
    return convertMetricClassestoMetricNames(getAllMetricClasses())
