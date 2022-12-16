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

    task_specific_metric_queries = {
        "task_parallelism", "count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)"
    }

    def __init__(self, configurations: Configurations):
        self.configs = configurations
        self.pandas_manager = PandasManager(self.configs)
        self.prometheus_manager = PrometheusManager(self.configs)
        self.file_writer = FileWriter(self.configs)

    def _fetch_experiment_start_end_timestamps(self, start_timestamp, end_timestamp):
        self.file_writer.write_start_end_time_to_file(start_timestamp, end_timestamp)

    def _fetch_single_column_metrics(self, start_timestamp, end_timestamp):
        for metric_name, metric_query in self.single_column_metric_queries.items():
            try:
                metric_df = self.prometheus_manager.get_pandas_dataframe_from_prometheus(metric_name, metric_query,
                                                                                         start_timestamp=start_timestamp,
                                                                                         end_timestamp=end_timestamp)
                self.pandas_manager.write_individual_metric_data_to_file(metric_name, metric_df)
            except:
                print(f"Error fetching individual metric {metric_name}")
                traceback.print_exc()

        print(f"Saved individual metrics at {self.configs.get_individual_data_directory()}/")

    def fetch_data(self):
        # print(f"Fetching data from {self.configs.prometheus_ip}:{self.configs.prometheus_port}")
        # self.file_writer.initialize_known_directories()

        # print("Writing timestamps")
        # start_timestamp, end_timestamp = self.prometheus_manager.get_prometheus_experiment_start_and_end_datetime()
        # self._fetch_experiment_start_end_timestamps(start_timestamp, end_timestamp)

        # print("Fetching individual data")
        # # Fetch individual data
        # self._fetch_single_column_metrics(start_timestamp, end_timestamp)
        #
        # print("Combining individual data")
        # # Combine individual data and write to file
        # self.pandas_manager.combine_individual_metrics_and_write_to_file()


        for key, item in self.task_specific_metric_queries.items():
            data = self.prometheus_manager.get_pandas_dataframe_from_prometheus("task_parallelism", self.task_specific_metric_queries.pop())
            print(data)

        print("Done fetching data")
