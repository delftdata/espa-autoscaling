from DataClasses import Autoscalers


class Metrics:
    """
    Helper class containing all available metrics used by the experiments
    """
    INPUT_RATE = "input_rate"
    INPUT_RATE_DEFAULT_RANGE = (0, None)
    TASKMANAGER = "taskmanager"
    TASKMANAGER_DEFAULT_RANGE = (0, None)
    LATENCY = "latency"
    LATENCY_DEFAULT_RANGE = (0, None)
    LAG = "lag"
    LAG_DEFAULT_RANGE = (0, None)
    INPUT_THROUGHPUT = "input_throughput"
    INPUT_THROUGHPUT_DEFAULT_RANGE = (0, None)
    OUTPUT_THROUGHPUT = "output_throughput"
    OUTPUT_THROUGHPUT_DEFAULT_RANGE = (0, None)
    CPU_LOAD = "CPU_load"
    CPU_LOAD_DEFAULT_RANGE = (0, 1)
    BACKPRESSURE = "backpressure"
    BACKPRESSURE_DEFAULT_RANGE = (0, None)
    BUSY_TIME = "busy_time"
    BUSY_TIME_DEFAULT_RANGE = (0, 1)
    IDLE_TIME = "idle_time"
    IDLE_TIME_DEFAULT_RANGE = (0, 1)

    VARGA_RELATIVE_LAG_CHANGE_RATE = "relative_lag_change_rate"
    VARGA_RELATIVE_LAG_CHANGE_RATE_DEFAULT_RANGE = (None, None)
    DS2_OPTIMAL_PARALLELISM = "optimal_parallelism"
    DS2_OPTIMAL_PARALLELISM_DEFAULT_RANGE = (0, None)

    @staticmethod
    def getDefaultRange(metric: str):
        if metric == Metrics.INPUT_RATE:
            return Metrics.INPUT_RATE_DEFAULT_RANGE
        elif metric == Metrics.TASKMANAGER:
            return Metrics.TASKMANAGER_DEFAULT_RANGE
        elif metric == Metrics.LATENCY:
            return Metrics.LATENCY_DEFAULT_RANGE
        elif metric == Metrics.LAG:
            return Metrics.LAG_DEFAULT_RANGE
        elif metric == Metrics.INPUT_THROUGHPUT:
            return Metrics.INPUT_THROUGHPUT_DEFAULT_RANGE
        elif metric == Metrics.OUTPUT_THROUGHPUT:
            return Metrics.OUTPUT_THROUGHPUT_DEFAULT_RANGE
        elif metric == Metrics.CPU_LOAD:
            return Metrics.CPU_LOAD_DEFAULT_RANGE
        elif metric == Metrics.BACKPRESSURE:
            return Metrics.BACKPRESSURE_DEFAULT_RANGE
        elif metric == Metrics.BUSY_TIME:
            return Metrics.BUSY_TIME_DEFAULT_RANGE
        elif metric == Metrics.IDLE_TIME:
            return Metrics.IDLE_TIME_DEFAULT_RANGE

        elif metric == Metrics.VARGA_RELATIVE_LAG_CHANGE_RATE:
            return Metrics.VARGA_RELATIVE_LAG_CHANGE_RATE_DEFAULT_RANGE
        elif metric == Metrics.DS2_OPTIMAL_PARALLELISM:
            return Metrics.DS2_OPTIMAL_PARALLELISM_DEFAULT_RANGE
        else:
            print(f"Error: did not recognize metric {metric}. Returning (None, None) ranges instead.")
            return None, None

    @staticmethod
    def getDefaultMetricClasses():
        return [
            Metrics.INPUT_RATE,
            Metrics.TASKMANAGER,
            Metrics.LATENCY,
            Metrics.LAG,
            Metrics.INPUT_THROUGHPUT,
            Metrics.OUTPUT_THROUGHPUT,
            Metrics.CPU_LOAD,
            Metrics.BACKPRESSURE,
            Metrics.BUSY_TIME,
            Metrics.IDLE_TIME,
        ]

    @staticmethod
    def getAllMetricClasses():
        """
        Get a list of all MetricClasses
        :return: list of all MetricClasses
        """
        return [
            Metrics.INPUT_RATE,
            Metrics.TASKMANAGER,
            Metrics.LATENCY,
            Metrics.LAG,
            Metrics.INPUT_THROUGHPUT,
            Metrics.OUTPUT_THROUGHPUT,
            Metrics.CPU_LOAD,
            Metrics.BACKPRESSURE,
            Metrics.BUSY_TIME,
            Metrics.IDLE_TIME,
            Metrics.VARGA_RELATIVE_LAG_CHANGE_RATE,
            Metrics.DS2_OPTIMAL_PARALLELISM,
        ]

    @staticmethod
    def getCustomMetricClasses():
        return [
            Metrics.VARGA_RELATIVE_LAG_CHANGE_RATE,
            Metrics.DS2_OPTIMAL_PARALLELISM,
        ]

    @staticmethod
    def getAllMetricClassesForAutoscaler(autoscaler: str):
        # if autoscaler in [Autoscalers.DS2_ORIGINAL, Autoscalers.DS2_UPDATED]:
        #     return Metrics.getDefaultMetricClasses()
        #     # return Metrics.getDefaultMetricClasses() + [Metrics.DS2_OPTIMAL_PARALLELISM]
        # elif autoscaler in [Autoscalers.VARGA1, Autoscalers.VARGA2]:
        #     return Metrics.getDefaultMetricClasses()
        #     # return Metrics.getDefaultMetricClasses() + [Metrics.VARGA_RELATIVE_LAG_CHANGE_RATE]
        # else:
        return Metrics.getDefaultMetricClasses()
    @staticmethod
    def isMetricClass(metric: str):
        return Metrics.getAllMetricClasses().__contains__(metric)

    @staticmethod
    def isDefaultMetricClass(metric: str):
        return Metrics.getDefaultMetricClasses().__contains__(metric)

    @staticmethod
    def isCustomMetricClass(metric: str):
        return Metrics.getCustomMetricClasses().__contains__(metric)