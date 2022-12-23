from DataClasses import Autoscalers


class Metrics:
    """
    Helper class containing all available metrics used by the experiments
    """

    metric_data = {
        "input_rate":           ("input rate", "rec/s", (0, None)),
        "taskmanager":          ("#taskmanagers", "", (0, None)),
        "latency":              ("latency", "seconds", (0, None)),
        "lag":                  ("lag", "records", (0, None)),
        "throughput":           ("input-throughput", "rec/s", (0, None)),
        "input_throughput":     ("input-throughput", "rec/s", (0, None)),
        "output_throughput":    ("output-throughput", "rec/s", (0, None)),
        "CPU_load":             ("CPU load", "percent", (0, 1)),
        "backpressure":         ("backpressure", "ms/s", (0, 1000)),
        "backpressure_time":    ("backpressure", "percent", (0, 1)),
        "busy_time":            ("busy time", "percent", (0, 1)),
        "idle_time":            ("idle time", "percent", (0, 1)),
    }

    @staticmethod
    def get_all_metrics() -> [str]:
        return list(Metrics.metric_data.keys())

    @staticmethod
    def is_metric_class(metric: str):
        return Metrics.get_all_metrics().__contains__(metric)



    @staticmethod
    def get_title_of_metric(metric: str):
        if Metrics.is_metric_class(metric):
            return Metrics.metric_data[metric][0]
        else:
            print(f"Error: did not recognize metric {metric}. Returning \"{metric}\" as title instead.")
            return ""

    @staticmethod
    def get_metric_title_mapping():
        metric_title_mapping = {}
        for metric in Metrics.get_all_metrics():
            metric_title_mapping[metric] = Metrics.get_title_of_metric(metric)
        return metric_title_mapping



    @staticmethod
    def get_unit_of_metric(metric: str):
        if Metrics.is_metric_class(metric):
            return Metrics.metric_data[metric][1]
        else:
            print(f"Error: did not recognize metric {metric}. Returning \"\" as unit instead.")
            return ""

    @staticmethod
    def get_metric_unit_mapping():
        metric_unit_mapping = {}
        for metric in Metrics.get_all_metrics():
            metric_unit_mapping[metric] = Metrics.get_unit_of_metric(metric)
        return metric_unit_mapping


    @staticmethod
    def get_default_range_of_metric(metric: str):
        if Metrics.is_metric_class(metric):
            return Metrics.metric_data[metric][2]
        else:
            print(f"Error: did not recognize metric {metric}. Returning (None, None) ranges instead.")
            return None, None

    @staticmethod
    def get_metric_range_mapping():
        metric_range_mapping = {}
        for metric in Metrics.get_all_metrics():
            metric_range_mapping[metric] = Metrics.get_default_range_of_metric(metric)
        return metric_range_mapping






