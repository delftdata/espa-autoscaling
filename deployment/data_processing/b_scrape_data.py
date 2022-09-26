from prometheus_api_client import PrometheusConnect, MetricsList, Metric, MetricSnapshotDataFrame, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
import os

"""
Fetch data of current experiment from prometheus server
"""


def scrape_data(prometheus_host_ip, query_being_run, autoscaler, cpu_percentage, load_pattern):
    prom = PrometheusConnect(url="http://" + prometheus_host_ip + ":9090", disable_ssl=True)

    start_time = parse_datetime("4h")
    end_time = parse_datetime("now")

    metric_query_dict = {
        "input_rate": "sum(rate(kafka_server_brokertopicmetrics_messagesin_total{topic=''}[1m]))",
        "latency": "avg(flink_taskmanager_job_task_operator_currentEmitEventTimeLag) / 1000",
        "throughput": "sum(flink_taskmanager_job_task_numRecordsInPerSecond{task_name=~\".*ink.*\"}) by (task_name)",
        "lag": "sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)",
        "CPU_load": "avg(flink_taskmanager_Status_JVM_CPU_Load)",
        "taskmanager": "sum(flink_jobmanager_numRegisteredTaskManagers)",
        "backpressure": "max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[1m]))",
        "idle_time": "avg(avg_over_time(flink_taskmanager_job_task_idleTimeMsPerSecond[1m])) / 1000",
        "busy_time": "avg(avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond[1m])) / 1000"
    }

    for metric in metric_query_dict:
        print("Retrieving data for: ", metric)

        metric_data = prom.custom_query_range(
            query=metric_query_dict[metric],
            start_time=start_time,
            end_time=end_time,
            step="15s",
        )

        metric_data[0]['metric'] = {'__name__': metric}

        metric_df = MetricRangeDataFrame(metric_data)
        path = "./experiment_data/individual_data/" + query_being_run + "/" + load_pattern + "/" + autoscaler + "/" + cpu_percentage
        if not os.path.exists(path):
            os.makedirs(path)
        metric_df.to_csv(path + "/" + metric + ".csv")
