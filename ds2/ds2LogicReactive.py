import requests
import json
import math
import time
import csv
import subprocess
import os
from kubernetes import client, config, utils

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

def extract_topic_input_rate(metrics_json):
    metrics = metrics_json.json()["data"]["result"]
    metrics_per_topic= {}
    for topic in metrics:
        if "topic" in topic['metric']:
            metrics_per_topic[topic['metric']['topic']] = float(topic['value'][1])
    return metrics_per_topic

avg_over_time = os.environ['AVG_OVER_TIME']
min_replicas = int(os.environ['MIN_REPLICAS'])
max_replicas = int(os.environ['MAX_REPLICAS'])
sleep_time = int(os.environ['SLEEP_TIME'])
container = os.environ["CONTAINER"]
query = os.environ["QUERY"]
job = os.environ["JOB"]
bidsQuery= os.environ["BIDSQUERY"]
min_replicas = int(os.environ['MIN_REPLICAS'])
max_replicas = int(os.environ['MAX_REPLICAS'])
cooldown = os.environ['COOLDOWN']

# sourceOperator= os.environ["SOURCEOPERATOR"]

# SourceOperator = "Source:_BidsSource"
# SourceOperator2 = "No"
# cooldown = "120s"
# min_replicas = 1
# max_replicas = 16
# sleep_time = 10
# bidsQuery = "yes"
# avg_over_time = "1m"
# query = "query-1"
# prometheus_address = "localhost:9090"
prometheus_address = "prometheus-server"
def run():
    while True:
        print('Executing DS2 Script')

        input_rate_query = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=rate(flink_taskmanager_job_task_operator_numRecordsIn[" + avg_over_time + "])")
        output_rate_query = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsOutPerSecond[" + avg_over_time + "])")
        busy_time_query = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond[" + avg_over_time + "])")
        number_of_processors_per_task = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")
        input_rate_kafka = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=rate(kafka_server_brokertopicmetrics_messagesin_total[1m])")
        true_processing = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=avg(flink_taskmanager_job_task_numRecordsOutPerSecond) by (task_name) / (avg(flink_taskmanager_job_task_busyTimeMsPerSecond) by (task_name) / 1000)")

        previous_scaling_event = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=deriv(flink_jobmanager_numRegisteredTaskManagers[" + cooldown + "])")
        previous_scaling_event = previous_scaling_event.json()["data"]["result"][0]["value"][1]
        print("taskmanager deriv: " + str(previous_scaling_event))


        input_rates_per_operator = extract_per_operator_metrics(input_rate_query, include_subtask=True)
        output_rates_per_operator = extract_per_operator_metrics(output_rate_query, include_subtask=True)
        busy_time_per_operator = extract_per_operator_metrics(busy_time_query, include_subtask=True)
        processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
        operators = list(processors_per_operator.keys())
        input_rate_kafka = extract_topic_input_rate(input_rate_kafka)
        source_true_processing = extract_per_operator_metrics(true_processing)

        print("Obtained metrics")
        print(operators)

        true_processing_rate = {}
        for key in input_rates_per_operator:
            true_processing_rate[key] = input_rates_per_operator[key] / (busy_time_per_operator[key] / 1000)

        true_output_rate = {}
        for key in output_rates_per_operator:
            true_output_rate[key] = output_rates_per_operator[key] / (busy_time_per_operator[key] / 1000)

        with open('./ds2_query_data/flink_rates_' + query + '.log', 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id", "operator_instance_id", "total_number_of_operator_instances", "epoch_timestamp", "true_processing_rate", "true_output_rate", "observed_processing_rate", "observed_output_rate"]
            writer.writerow(header)

            timestamp = time.time_ns()
            for key in input_rates_per_operator:
                formatted_key = key.split(" ")
                operator, operator_id = formatted_key[0], formatted_key[1]
                row = [operator, operator_id, int(processors_per_operator[operator]), timestamp, true_processing_rate[key], true_output_rate[key], input_rates_per_operator[key], output_rates_per_operator[key]]
                writer.writerow(row)
        print("Wrote rates file")

        operator_set = set()
        topology_order = []
        topology_parallelism = {}
        with open('./ds2_query_data/flink_topology_' + query + '.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\n')
            for index, row in enumerate(reader):
                if index == 0:
                    continue
                row_values = row[0].split(",")
                topology_parallelism[row_values[0]] = row_values[2]
                topology_parallelism[row_values[3]] = row_values[5]
                if row_values[0] not in operator_set:
                    topology_order.append(row_values[0])
                    operator_set.add(row_values[0])
                if row_values[3] not in operator_set:
                    topology_order.append(row_values[3])
                    operator_set.add(row_values[3])


        with open('./ds2_query_data/flink_topology_' + query + '.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id1","operator_name1","total_number_of_operator_instances1","operator_id2","operator_name2","total_number_of_operator_instances2"]
            writer.writerow(header)
            for i in range(0, len(topology_order) - 1):
                row = [topology_order[i], topology_order[i], int(processors_per_operator[topology_order[i]]), topology_order[i + 1], topology_order[i + 1], int(processors_per_operator[topology_order[i + 1]])]
                writer.writerow(row)
        print("Wrote topology file")

        ds2_model_result = subprocess.run(["cargo", "run", "--release", "--bin", "policy", "--", "--topo", "ds2_query_data/flink_topology_" + query + ".csv", "--rates", "ds2_query_data/flink_rates_" + query + ".log", "--system", "flink"], capture_output=True)
        output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
        output_text_values = output_text.split(",")
        suggested_parallelism = {}

        for i in range(0, len(output_text_values), 2):
            suggested_parallelism[output_text_values[i]] = output_text_values[i + 1].replace("\"", "")

        print("DS2 model result")
        print(suggested_parallelism)

        source1_parallelism = 0
        source2_parallelism = 0
        if bidsQuery == "yes":
            source1_parallelism = math.ceil(input_rate_kafka['bids_topic'] / source_true_processing['Source:_BidsSource'])
        if bidsQuery == "no":
            source1_parallelism = math.ceil(input_rate_kafka['auction_topic'] / source_true_processing['Source:_AuctionSource'])
            source2_parallelism = math.ceil(input_rate_kafka['person_topic'] / source_true_processing['Source:_PersonSource'])

        print("source 1 parallelism", source1_parallelism)
        print("source 2 parallelism", source2_parallelism)

        number_of_taskmanagers = max(source2_parallelism, source1_parallelism)

        if number_of_taskmanagers > max_replicas:
            number_of_taskmanagers = 16
        if number_of_taskmanagers <= 0:
            number_of_taskmanagers = 1

        for key, val in suggested_parallelism.items():
            number_of_taskmanagers = max(number_of_taskmanagers, int(val))

        print("Suggested number of taskmanagers", number_of_taskmanagers)

        # autenticate with kubernetes API
        config.load_incluster_config()
        v1 = client.AppsV1Api()

        # retrieving current number of taskmanagers from kubernetes API
        current_number_of_taskmanagers = None
        ret = v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True,
                                            field_selector="metadata.name=flink-taskmanager")
        for i in ret.items:
            current_number_of_taskmanagers = int(i.spec.replicas)
        print("current number of taskmanagers: " + str(current_number_of_taskmanagers))
        if float(previous_scaling_event) == 0:
            print("rescaling to", number_of_taskmanagers)
            # scale taskmanager
            new_number_of_taskmanagers = number_of_taskmanagers
            body = {"spec": {"replicas": new_number_of_taskmanagers}}
            api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
            v1 = client.BatchV1Api()
        else:
            print("in cooldown")

        time.sleep(sleep_time)


def keep_running():
    try:
        run()
    except:
        time.sleep(10)
        keep_running()

keep_running()