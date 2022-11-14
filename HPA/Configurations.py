import os


class Configurations:
    # Whether to use Flink Reactive for scaling operators
    USE_FLINK_REACTIVE = os.environ.get("USE_FLINK_REACTIVE", "False").lower() in ["true", "1", "t"]
    # Address of the prometheus server
    PROMETHEUS_SERVER = os.environ.get("PROMETHEUS_SERVER", "prometheus-server")
    FLINK_JOBMANAGER_SERVER = os.environ.get("FLINK_JOBMANAGER_SERVER", "flink-jobmanager-rest:8081")

    # Minimum amount of taskmanagers
    MIN_TASKMANAGERS = int(os.environ.get("MIN_TASKMANAGERS", 1))
    # Maximum amount of taskmanagers
    MAX_TASKMANAGERS = int(os.environ.get("MAX_TASKMANAGERS", 16))

    METRIC_AGGREGATION_PERIOD_SECONDS = int(os.environ.get("METRIC_AGGREGATION_PERIOD_SECONDS", 20))

    HPA_SYNC_PERIOD_SECONDS = int(os.environ.get("HPA_SYNC_PERIOD", 15))  # default = 15s
    SCALE_DOWN_WINDOW_SECONDS = int(os.environ.get("SCALE_DOWN_WINDOW_SECONDS", 25))

    # Range of parallelism per operator
    MAX_PARALLELISM = int(os.environ.get("MAX_PARALLELISM", 1))
    MIN_PARALLELISM = int(os.environ.get("MIN_PARALLELISM", 1))

    HPA_TARGET_VALUE = float(os.environ.get("HPA_TARGET_VALUE", 0.7))
