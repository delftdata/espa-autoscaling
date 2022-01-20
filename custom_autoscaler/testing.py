import requests
import json

def extract_per_operator_metrics(metrics_json):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
    return metrics_per_operator

avg_over_time = "2m"
input_rate_query = requests.get("http://localhost:9090/api/v1/query?query=sum(avg_over_time(flink_taskmanager_job_task_operator_numRecordsIn[1m])) by (task_name)")
output_rate_query = requests.get("http://localhost:9090/api/v1/query?query=sum(avg_over_time(flink_taskmanager_job_task_operator_numRecordsOut[1m])) by (task_name)")
flink_input_rate = requests.get("http://localhost:9090/api/v1/query?query=flink_taskmanager_job_task_operator_KafkaConsumer_records_consumed_rate")
number_of_processors_per_task = requests.get("http://localhost:9090/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")

print(input_rate_query.text)
print(input_rate_query.json()["data"]["result"])

input_rates_per_operator = extract_per_operator_metrics(input_rate_query)
output_rates_per_operator = extract_per_operator_metrics(output_rate_query)
processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
operators = list(processors_per_operator.keys())

print(operators)

output_per_processor = dict()
for operator in operators:
    output_per_processor[operator] = output_rates_per_operator[operator] / processors_per_operator[operator]

print(output_rates_per_operator)
print(output_per_processor)

