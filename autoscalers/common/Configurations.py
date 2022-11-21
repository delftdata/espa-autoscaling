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
    ITERATION_PERIOD_SECONDS = int(os.environ.get("ITERATION_PERIOD_SECONDS", 15))

    NONREACTIVE_CONTAINER = os.environ.get("NONREACTIVE_CONTAINER", "9923/experiments:31")
    NONREACTIVE_QUERY = int(os.environ.get("NONREACTIVE_QUERY",  "1"))
    NONREACTIVE_TIME_AFTER_DELETE_JOB = int(os.environ.get("NONREACTIVE_TIME_AFTER_DELETE_JOB",  "4"))
    NONREACTIVE_TIME_AFTER_DELETE_POD = int(os.environ.get('NONREACTIVE_TIME_AFTER_DELETE_POD', "4"))
    NONREACTIVE_TIME_AFTER_SAVEPOINT = int(os.environ.get('NONREACTIVE_TIME_AFTER_SAVEPOINT', "4"))

    def printConfigurations(self):
        print(f"\tUSE_FLINK_REACTIVE: {self.USE_FLINK_REACTIVE}")
        print(f"\tPROMETHEUS_SERVER: {self.PROMETHEUS_SERVER}")
        print(f"\tFLINK_JOBMANAGER_SERVER: {self.FLINK_JOBMANAGER_SERVER}")
        print(f"\tMAX_PARALLELISM: {self.MAX_PARALLELISM}")
        print(f"\tMIN_PARALLELISM: {self.MIN_PARALLELISM}")
        print(f"\tMETRIC_AGGREGATION_PERIOD_SECONDS: {self.METRIC_AGGREGATION_PERIOD_SECONDS}")
        print(f"\tCOOLDOWN_PERIOD_SECONDS: {self.COOLDOWN_PERIOD_SECONDS}")
        print(f"\tITERATION_PERIOD_SECONDS: {self.ITERATION_PERIOD_SECONDS}")
        print(f"\tNONREACTIVE_TIME_AFTER_DELETE_JOB: {self.NONREACTIVE_TIME_AFTER_DELETE_JOB}")
        print(f"\tNONREACTIVE_TIME_AFTER_DELETE_POD: {self.NONREACTIVE_TIME_AFTER_DELETE_POD}")
        print(f"\tNONREACTIVE_TIME_AFTER_SAVEPOINT: {self.NONREACTIVE_TIME_AFTER_SAVEPOINT}")


