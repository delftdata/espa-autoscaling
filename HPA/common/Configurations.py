import os


class Configurations:
    # Whether to use Flink Reactive for scaling operators
    USE_FLINK_REACTIVE = os.environ.get("USE_FLINK_REACTIVE", "False").lower() in ["true", "1", "t"]
    # Address of the prometheus server
    PROMETHEUS_SERVER = os.environ.get("PROMETHEUS_SERVER", "prometheus-server")
    FLINK_JOBMANAGER_SERVER = os.environ.get("FLINK_JOBMANAGER_SERVER", "flink-jobmanager-rest:8081")

    METRIC_AGGREGATION_PERIOD_SECONDS = int(os.environ.get("METRIC_AGGREGATION_PERIOD_SECONDS", 10))

    HPA_SYNC_PERIOD_SECONDS = int(os.environ.get("HPA_SYNC_PERIOD", 15))  # default = 15s
    SCALE_DOWN_WINDOW_SECONDS = int(os.environ.get("SCALE_DOWN_WINDOW_SECONDS", 300))

    # Range of parallelism per operator
    MAX_PARALLELISM = int(os.environ.get("MAX_PARALLELISM", 16))
    MIN_PARALLELISM = int(os.environ.get("MIN_PARALLELISM", 1))

    HPA_TARGET_VALUE = float(os.environ.get("HPA_TARGET_VALUE", 0.7))

    HPA_MAX_INITIALIZATION_TRIES = int(os.environ.get("HPA_MAX_INITIALIZATION_TRIES", 5))

    HPA_COOLDOWN_PERIOD_SECONDS = int(os.environ.get("HPA_COOLDOWN_PERIOD_SECONDS", 120))

    def printConfigurations(self):
        print(f"\tUSE_FLINK_REACTIVE: {self.USE_FLINK_REACTIVE}")
        print(f"\tPROMETHEUS_SERVER: {self.PROMETHEUS_SERVER}")
        print(f"\tFLINK_JOBMANAGER_SERVER: {self.FLINK_JOBMANAGER_SERVER}")
        print(f"\tMAX_PARALLELISM: {self.MAX_PARALLELISM}")
        print(f"\tMIN_PARALLELISM: {self.MIN_PARALLELISM}")
        print(f"\tMETRIC_AGGREGATION_PERIOD_SECONDS: {self.METRIC_AGGREGATION_PERIOD_SECONDS}")
        print(f"\tHPA_SYNC_PERIOD_SECONDS: {self.HPA_SYNC_PERIOD_SECONDS}")
        print(f"\tSCALE_DOWN_WINDOW_SECONDS: {self.SCALE_DOWN_WINDOW_SECONDS}")
        print(f"\tHPA_TARGET_VALUE: {self.HPA_TARGET_VALUE}")
        print(f"\tHPA_COOLDOWN_PERIOD_SECONDS: {self.HPA_COOLDOWN_PERIOD_SECONDS}")
