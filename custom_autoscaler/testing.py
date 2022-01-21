import requests
import json
import math


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

# latency per processor
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
        ans += input_rates[operator] * average_latency(input_rate=input_rates[operator], output_rate=output_rates[operator], processors=processors[operator])
    ans = ans / system_input_rate

    return ans


avg_over_time = "2m"
input_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg(rate(flink_taskmanager_job_task_operator_numRecordsIn[1m])) by (task_name)")
output_rate_query = requests.get(
    "http://localhost:9090/api/v1/query?query=avg(rate(flink_taskmanager_job_task_operator_numRecordsOut[1m])) by (task_name)")
flink_input_rate = requests.get(
    "http://localhost:9090/api/v1/query?query=sum(flink_taskmanager_job_task_operator_KafkaConsumer_records_consumed_rate)")
number_of_processors_per_task = requests.get(
    "http://localhost:9090/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")



input_rates_per_operator = extract_per_operator_metrics(input_rate_query)
output_rates_per_operator = extract_per_operator_metrics(output_rate_query)
processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
operators = list(processors_per_operator.keys())
flink_input_rate_formatted = float(flink_input_rate.json()["data"]["result"][0]["value"][1])

# set input rate of source equal to output rate, output rate of sink equal to input rate
for operator in operators:
    if input_rates_per_operator[operator] == 0:
        input_rates_per_operator[operator] = output_rates_per_operator[operator]
    if output_rates_per_operator[operator] == 0:
        output_rates_per_operator[operator] = input_rates_per_operator[operator]
    output_rates_per_operator[operator] += 10


# divide output per operator by number of processors
output_per_processor = dict()
for operator in operators:
    output_per_processor[operator] = output_rates_per_operator[operator] / processors_per_operator[operator]



# print(input_rates_per_operator)
# print(output_per_processor)
# print(processors_per_operator)
# print(flink_input_rate_formatted)
# {'Throughput_Logger': 235666.66666666663, 'Expensive_Computation': 235622.6333333333, 'Source:_Kafka': 0.0, 'Sink:_Sink': 235613.41666666666}
# {'Throughput_Logger': 0.0, 'Expensive_Computation': 117813.50833333335, 'Source:_Kafka': 235666.66666666663, 'Sink:_Sink': 0.0}
# {'Throughput_Logger': 1.0, 'Expensive_Computation': 2.0, 'Source:_Kafka': 1.0, 'Sink:_Sink': 2.0}
# 629.8022420959819


#
# print(drs_pi_term(input_rates_per_operator['Expensive_Computation'], output_per_processor['Expensive_Computation'],
#                   processors_per_operator['Expensive_Computation']))

print(operators)
print(input_rates_per_operator)
print(output_per_processor)
print(processors_per_operator)
print(flink_input_rate_formatted)
print(expected_latency_of_system(operators, input_rates_per_operator, output_per_processor, processors_per_operator, flink_input_rate_formatted))



# to do answer are not consistent
# output rate is not the same as processing time, processing time is big problem output 10 tuples per second does not mean it takes 0.1 seconds to process a tuple
# look into latency metrics latency = processing time for operators
