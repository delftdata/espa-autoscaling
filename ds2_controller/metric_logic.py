import requests
import json
import math
import time
import csv


# extract metrics from prometheus query
def extract_per_operator_metrics(metrics_json, include_subtask=False):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        if include_subtask:
            metrics_per_operator[operator["metric"]["task_name"] + " " + operator["metric"]["subtask_index"]] = float(
                operator["value"][1])
        else:
            metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
    return metrics_per_operator


avg_over_time = "1m"
input_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsInPerSecond[1m])")
output_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsOutPerSecond[1m])")
busy_time_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond[1m])")
number_of_processors_per_task = requests.get(
    "http://localhost:9090/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")

input_rates_per_operator = extract_per_operator_metrics(input_rate_query, include_subtask=True)
output_rates_per_operator = extract_per_operator_metrics(output_rate_query, include_subtask=True)
busy_time_per_operator = extract_per_operator_metrics(busy_time_query, include_subtask=True)
processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
operators = list(processors_per_operator.keys())

# might not be needed after upgrading source function
for key in busy_time_per_operator:
    if math.isnan(busy_time_per_operator[key]):
        busy_time_per_operator[key] = 200

# print(input_rates_per_operator)
# print(output_rates_per_operator)
# print(busy_time_per_operator)
# print(processors_per_operator)
# print(operators)

true_processing_rate = {}
for key in input_rates_per_operator:
    true_processing_rate[key] = input_rates_per_operator[key] / (busy_time_per_operator[key] / 1000)

true_output_rate = {}
for key in output_rates_per_operator:
    true_output_rate[key] = output_rates_per_operator[key] / (busy_time_per_operator[key] / 1000)

# print(true_processing_rate)
# print(true_output_rate)


with open('./examples/offline/flink_test_rates_2_tm.log', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ["# operator_id", "operator_instance_id", "total_number_of_operator_instances", "epoch_timestamp", "true_processing_rate", "true_output_rate", "observed_processing_rate", "observed_output_rate"]
    writer.writerow(header)

    timestamp = time.time_ns()
    for key in input_rates_per_operator:
        formatted_key = key.split(" ")
        operator, operator_id = formatted_key[0], formatted_key[1]
        row = [operator, operator_id, int(processors_per_operator[operator]), timestamp, true_processing_rate[key], true_output_rate[key], input_rates_per_operator[key], output_rates_per_operator[key]]
        writer.writerow(row)



