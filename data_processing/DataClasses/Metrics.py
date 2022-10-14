class Metrics:
    """
    Helper class containing all available metrics used by the experiments
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
            Metrics.THROUGHPUT,
            Metrics.CPU_LOAD,
            Metrics.BACKPRESSURE,
            Metrics.BUSY_TIME,
            Metrics.IDLE_TIME
        ]

    @staticmethod
    def isMetricClass(metric: str):
        return Metrics.getAllMetricClasses().__contains__(metric)
