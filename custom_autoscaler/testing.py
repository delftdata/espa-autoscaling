import requests
import json
import math

def MinProcessors(T_max, system_input_rate, input_rates_per_operator, processing_rates_per_operator, operators):
    assigned_processors = {}
    total_processors = 0
    min_latency = 0
    for operator in operators:
        assigned_processors[operator] = math.floor(
            input_rates_per_operator[operator] / processing_rates_per_operator[operator]) + 1
        total_processors += assigned_processors[operator]
        min_latency += 1 / processing_rates_per_operator[operator]
    if min_latency > T_max:
        print("here")
        return Exception()
    while expected_latency_of_system(operators, input_rates_per_operator, processing_rates_per_operator, assigned_processors, system_input_rate) > T_max:
        total_processors += 1
        assigned_processors = AssignProcessors(total_processors, system_input_rate, input_rates_per_operator, processing_rates_per_operator, operators)
    return assigned_processors


def AssignProcessors(K_max, system_input_rate, input_rates_per_operator, processing_rates_per_operator, operators):
    assigned_processors = {}
    for operator in operators:
        assigned_processors[operator] = math.floor(
            input_rates_per_operator[operator] / processing_rates_per_operator[operator]) + 1
    sum_processors = sum(assigned_processors.values())
    if sum_processors > K_max:
        return Exception()
    while sum_processors <= K_max:
        highest_latency = 0
        highest_latency_operator = None
        for operator in operators:
            latency_improvement = input_rates_per_operator[operator](
                average_latency(input_rates_per_operator[operator], processing_rates_per_operator[operator],
                                assigned_processors[operator]) - average_latency(input_rates_per_operator[operator], processing_rates_per_operator[operator],
                                assigned_processors[operator] + 1))
            if latency_improvement > highest_latency:
                highest_latency = latency_improvement
                highest_latency_operator = operator
        assigned_processors[highest_latency_operator] += 1
    return assigned_processors


# normalization factor
def drs_pi_term(input_rate, output_rate, processors):
    ans = 0
    rho = input_rate / (output_rate * processors)
    for i in range(0, int(processors)):
        ans += math.pow((math.pow((processors * rho), i) / math.factorial(i)) + (
                math.pow((processors * rho), processors) / (math.factorial(int(processors)) * (1 - rho))), -1)
    return ans


# queueing delay
def drs_queue_delay_operator(input_rate, output_rate, processors):
    ans = math.inf
    rho = input_rate / (output_rate * processors)
    if rho <= 1.0:
        ans = (drs_pi_term(input_rate, output_rate, processors) * math.pow((processors * rho), processors)) / (
                math.factorial(int(processors)) * math.pow((1 - rho), 2) * output_rate * processors)
    return ans


# latency per operator
def average_latency(input_rate, output_rate, processors):
    ans = drs_queue_delay_operator(input_rate, output_rate, processors) + (1 / output_rate)
    return ans


# extract metrics from prometheus query
def extract_per_operator_metrics(metrics_json):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_operator = {}
    for operator in metrics:
        metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
    return metrics_per_operator


# latency of entire system
def expected_latency_of_system(operators, input_rates, output_rates, processors, system_input_rate):
    ans = 0
    for operator in operators:
        ans += input_rates[operator] * average_latency(input_rate=input_rates[operator],
                                                       output_rate=output_rates[operator],
                                                       processors=processors[operator])
    ans = ans / system_input_rate

    return ans


avg_over_time = "2m"
input_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg(rate(flink_taskmanager_job_task_operator_numRecordsIn[1m])) by (task_name)")
output_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg(rate(flink_taskmanager_job_task_operator_numRecordsOut[1m])) by (task_name)")
processing_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg(flink_taskmanager_job_task_operator_myHistogramExpensive{quantile = \"0.5\"}) by (task_name)")
flink_input_rate = requests.get(
    "http://localhost:9090/api/v1/query?query=sum(flink_taskmanager_job_task_operator_KafkaConsumer_records_consumed_rate)")
number_of_processors_per_task = requests.get(
    "http://localhost:9090/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")

input_rates_per_operator = extract_per_operator_metrics(input_rate_query)
output_rates_per_operator = extract_per_operator_metrics(output_rate_query)
processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
processing_rate_per_operator = extract_per_operator_metrics(processing_rate_query)
operators = list(processors_per_operator.keys())
flink_input_rate_formatted = float(flink_input_rate.json()["data"]["result"][0]["value"][1])

# set input rate of source equal to output rate, output rate of sink equal to input rate
for operator in operators:
    if input_rates_per_operator[operator] == 0:
        input_rates_per_operator[operator] = output_rates_per_operator[operator]

processing_rate_max = 700000
for operator in operators:
    if operator not in processing_rate_per_operator:
        processing_rate_per_operator[operator] = processing_rate_max
    else:
        if processing_rate_per_operator[operator] == 0:
            processing_rate_per_operator[operator] = processing_rate_max

# print(drs_pi_term(input_rates_per_operator['Expensive_Computation'], output_per_processor['Expensive_Computation'],
#                   processors_per_operator['Expensive_Computation']))
# operators = ['Expensive_Computation', 'Source:_Kafka', 'Sink:_Sink']
# input_rates_per_operator = {'Expensive_Computation': 10000, 'Source:_Kafka': 10000, 'Sink:_Sink': 10000}
# output_rates_per_operator = {'Expensive_Computation': 2855.110169491525, 'Source:_Kafka': 5702.474576271186, 'Sink:_Sink': 0.0}
# processing_rate_per_operator = {'Expensive_Computation': 20000, 'Source:_Kafka': 20000, 'Sink:_Sink': 20000}
# processors_per_operator = {'Expensive_Computation': 3.0, 'Source:_Kafka': 1.0, 'Sink:_Sink': 1.0}
# flink_input_rate_formatted = 10000
processing_rate_per_operator = {'Expensive_Computation': 20000, 'Source:_Kafka': 100000, 'Sink:_Sink': 100000}


print(operators)
print("input")
print(input_rates_per_operator)
print("output_rate")
print(output_rates_per_operator)
print("processing_rate")
print(processing_rate_per_operator)
print("processors per operator")
print(processors_per_operator)
print("input rate of system")
print(flink_input_rate_formatted)
print(expected_latency_of_system(operators, input_rates_per_operator, processing_rate_per_operator,
                                 processors_per_operator, flink_input_rate_formatted))
T_max = 0.00007
print(MinProcessors(T_max, flink_input_rate_formatted, input_rates_per_operator, processing_rate_per_operator, operators))
