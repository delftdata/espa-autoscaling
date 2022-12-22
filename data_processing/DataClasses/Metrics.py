from DataClasses import Autoscalers


class Metrics:
    """
    Helper class containing all available metrics used by the experiments
    """

    metric_range_mapping = {
        "input_rate": (0, None),
        "taskmanager": (0, None),
        "latency": (0, None),
        "lag": (0, None),
        "input_throughput": (0, None),
        "output_throughput": (0, None),
        "CPU_load": (0, 1),
        "backpressure": (0, None),
        "busy_time": (0, 1),
        "idle_time": (0, 1),
    }

    @staticmethod
    def get_default_metric_range_of_metric(metric: str):
        if Metrics.isMetricClass(metric):
            return Metrics.metric_range_mapping[metric]
        else:
            print(f"Error: did not recognize metric {metric}. Returning (None, None) ranges instead.")
            return None, None

    @staticmethod
    def get_all_metric_classes():
        return Metrics.metric_range_mapping.keys()

    @staticmethod
    def is_metric_class(metric: str):
        return Metrics.get_all_metric_classes().__contains__(metric)
