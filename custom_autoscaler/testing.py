import requests
import json
import math


def drs_pi_term(input_rate, output_rate, processors):
    ans = 0
    rho = input_rate / (output_rate * processors)
    for i in range(0, processors):
        ans += math.pow((math.pow((processors * rho), i) / math.factorial(i)) + (
                    math.pow((processors * rho), processors) / (math.factorial(processors) * (1 - rho))), -1)
    return ans


def drs_queue_delay_operator(input_rate, output_rate, processors):
    ans = math.inf
    rho = input_rate / (output_rate * processors)
    if rho < 1:
        ans = (drs_pi_term(input_rate, output_rate, processors) * math.pow((processors * rho), processors)) / (
                    math.factorial(processors) * math.pow((1 - rho), 2) * output_rate * processors)
    return ans

def average_latency(input_rate, output_rate, processors):
    ans = drs_queue_delay_operator(input_rate, output_rate, processors) + (1 / output_rate)


def extract_per_operator_metrics(metrics_json):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
    return metrics_per_operator

def expected_latency_of_system(operators, input_rates, output_rates, processors, system_input_rate):
    ans = 0
    for operator in operators:
        ans += input_rates[operator] * average_latency(input_rate=input_rates[operator], output_rate=output_rates[operator], processors=processors)
    ans = ans / system_input_rate

    return ans


avg_over_time = "2m"
input_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=sum(avg_over_time(flink_taskmanager_job_task_operator_numRecordsIn[1m])) by (task_name)")
output_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=sum(avg_over_time(flink_taskmanager_job_task_operator_numRecordsOut[1m])) by (task_name)")
flink_input_rate = requests.get(
    "http://localhost:9090/api/v1/query?query=flink_taskmanager_job_task_operator_KafkaConsumer_records_consumed_rate")
number_of_processors_per_task = requests.get(
    "http://localhost:9090/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")

print(input_rate_query.text)
print(input_rate_query.json()["data"]["result"])

input_rates_per_operator = extract_per_operator_metrics(input_rate_query)
output_rates_per_operator = extract_per_operator_metrics(output_rate_query)
processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
operators = list(processors_per_operator.keys())

output_per_processor = dict()
for operator in operators:
    output_per_processor[operator] = output_rates_per_operator[operator] / processors_per_operator[operator]

print(drs_pi_term(input_rates_per_operator['Expensive_Computation'], output_per_processor['Expensive_Computation'],
                  processors_per_operator['Expensive_Computation']))
