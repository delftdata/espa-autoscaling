from PandasManager import PandasManager
from PrometheusManager import PrometheusManager
from FileWriter import FileWriter
from Configuration import Configurations
import traceback


class MetricFetcher:
    configs: Configurations
    pandas_manager: PandasManager
    prometheus_manager: PrometheusManager
    file_writer: FileWriter

    # Metrics that are aggregated over the entire system. Results fetched from prometheus only contains a single column.
    single_column_metric_queries = {
        "input_rate": "sum(rate(kafka_server_brokertopicmetrics_messagesin_total{topic=''}[1m]))",
        "latency": "avg(flink_taskmanager_job_task_operator_currentEmitEventTimeLag) / 1000",
        "throughput": "sum(flink_taskmanager_job_task_numRecordsInPerSecond{task_name=~\".*ink.*\"}) by (task_name)",
        "lag": "sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * "
               "flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)",
        "CPU_load": "avg(flink_taskmanager_Status_JVM_CPU_Load)",
        "taskmanager": "sum(flink_jobmanager_numRegisteredTaskManagers)",
        "backpressure": "max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[1m]))",
        "idle_time": "avg(avg_over_time(flink_taskmanager_job_task_idleTimeMsPerSecond[1m])) / 1000",
        "busy_time": "avg(avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond[1m])) / 1000"
    }

    # Metrics that are aggregated per task_name. Results fetched form prometheus contain as many colums as the amount of
    # tasks
    task_specific_metric_queries = {
        "task_parallelism": "count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)",
    }

    def __init__(self, configurations: Configurations):
        """
        Constructor of the MetricFetcher
        """
        self.configs = configurations
        self.pandas_manager = PandasManager(self.configs)
        self.prometheus_manager = PrometheusManager(self.configs)
        self.file_writer = FileWriter(self.configs)

    def _fetch_experiment_start_end_timestamps(self, timestamp_file=None):
        """
        Fetch the start and end time of the current experiment, write them to file and return them.
        """
        if timestamp_file:
            print(f"Fetching timestamps from {timestamp_file} and writing them to file")
            start_timestamp, end_timestamp = self.file_writer.read_start_end_time_from_file(timestamp_file)
        else:
            print("Determining default timestamps timestamps and writing them to file")
            start_timestamp, end_timestamp = self.prometheus_manager.get_prometheus_experiment_start_and_end_datetime()
        self._fetch_experiment_start_end_timestamps(start_timestamp, end_timestamp)

        self.file_writer.write_start_end_time_to_file(start_timestamp, end_timestamp)
        return start_timestamp, end_timestamp

    def _fetch_single_column_metrics(self, start_timestamp, end_timestamp):
        """
        Fetch the data of the single_column_metric_queries and write them to file.
        """
        for metric_name, metric_query in self.single_column_metric_queries.items():
            try:
                metric_df = self.prometheus_manager.get_pandas_dataframe_from_prometheus(
                    metric_query, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
                self.pandas_manager.write_individual_metric_data_to_file(metric_name, metric_df)
            except:
                print(f"Error fetching individual metric {metric_name}")
                traceback.print_exc()
        print(f"Saved individual metrics at {self.configs.get_individual_data_directory()}/")

    def _fetch_task_specific_column_metrics(self, start_timestamp, end_timestamp):
        """
        Fetch the data of the task_specific_metric_queries and write them to file.
        """
        for metric_name, metric_query in self.task_specific_metric_queries.items():
            try:
                metric_data = self.prometheus_manager.get_pandas_dataframe_from_prometheus(
                    metric_query, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
                self.pandas_manager.write_task_specific_metric_data_to_file(metric_name, metric_data)
            except:
                print(f"Error fetching task specific metric {metric_name}")
                traceback.print_exc()
        print(f"Saved task specific metrics at {self.configs.get_individual_data_directory()}/")


    def fetch_data(self, timestamp_file=None):
        """
        Fetch all data of an experiment.
        param: timestamp-file: default=None. If provided the timestamps determining the timeframe where to fetch data
        from a taken from this file. If not provided, timestamps are generated from [now - experiment_length, now].
        This function
        - Determines timestamps and write them to a file
        - Fetches all results from the single_column_metric_queries and writes them to file
        - Fetches all results from the task_specific_metric_queries and writes them to file
        - Combines all results in a single file and writes it to file
        """
        print(f"Fetching data from {self.configs.prometheus_ip}:{self.configs.prometheus_port}")
        self.file_writer.initialize_known_directories()

        start_timestamp, end_timestamp = self._fetch_experiment_start_end_timestamps(timestamp_file)

        print("Fetching individual data")
        # Fetch individual data
        self._fetch_single_column_metrics(start_timestamp, end_timestamp)

        print("Fetching task-specific data")
        # Fetch individual data
        self._fetch_task_specific_column_metrics(start_timestamp, end_timestamp)

        print("Combining individual data")
        # Combine individual data and write to file
        self.pandas_manager.combine_individual_metrics_and_write_to_file()

        print("Done fetching data")
