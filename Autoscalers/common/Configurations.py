import os


class Configurations:
    # Whether to use Flink Reactive for scaling operators
    USE_FLINK_REACTIVE = os.environ.get("USE_FLINK_REACTIVE", "False").lower() in ["true", "1", "t"]
    # Address of the prometheus server
    PROMETHEUS_SERVER = os.environ.get("PROMETHEUS_SERVER", "prometheus-server")
    # Address of the jobmanager server
    FLINK_JOBMANAGER_SERVER = os.environ.get("FLINK_JOBMANAGER_SERVER", "flink-jobmanager-rest:8081")

    # Range of parallelism per operator
    MAX_PARALLELISM = int(os.environ.get("MAX_PARALLELISM", 16))
    MIN_PARALLELISM = int(os.environ.get("MIN_PARALLELISM", 1))
    
    METRIC_AGGREGATION_PERIOD_SECONDS = int(os.environ.get("METRIC_AGGREGATION_PERIOD_SECONDS", 10))
    COOLDOWN_PERIOD_SECONDS = int(os.environ.get("COOLDOWN_PERIOD_SECONDS", 120))

    MAX_INITIALIZATION_TRIES = int(os.environ.get("MAX_INITIALIZATION_TRIES", 5))


    def printConfigurations(self):
        print(f"\tUSE_FLINK_REACTIVE: {self.USE_FLINK_REACTIVE}")
        print(f"\tPROMETHEUS_SERVER: {self.PROMETHEUS_SERVER}")
        print(f"\tFLINK_JOBMANAGER_SERVER: {self.FLINK_JOBMANAGER_SERVER}")
        print(f"\tMAX_PARALLELISM: {self.MAX_PARALLELISM}")
        print(f"\tMIN_PARALLELISM: {self.MIN_PARALLELISM}")
        print(f"\tMETRIC_AGGREGATION_PERIOD_SECONDS: {self.METRIC_AGGREGATION_PERIOD_SECONDS}")
        print(f"\tCOOLDOWN_PERIOD_SECONDS: {self.COOLDOWN_PERIOD_SECONDS}")
        print(f"\tHPA_MAX_INITIALIZATION_TRIES: {self.MAX_INITIALIZATION_TRIES}")

