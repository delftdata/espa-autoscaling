import requests
import json
import math
import time
import csv
import subprocess
import os
import traceback
from kubernetes import client, config, utils

# extract metrics from prometheus query
def \
        extract_per_operator_metrics(metrics_json, include_subtask=False):
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
min_replicas = int(os.environ['MIN_REPLICAS'])
max_replicas = int(os.environ['MAX_REPLICAS'])
cooldown = os.environ['COOLDOWN']
overprovisioning_factor = float(os.environ["OVERPROVISIONING_FACTOR"])
lag_processing_time = int(os.environ['LAG_PROCESSING_TIME'])
scale_up_lag_threshold = float(os.environ["SCALE_UP_LAG_THRESHOLD"])
scale_down_lag_threshold = float(os.environ["SCALE_DOWN_LAG_THRESHOLD"])



# lag_processing_time = 120
# cooldown = "120s"
# min_replicas = 1
# max_replicas = 16
# sleep_time = 10
# avg_over_time = "1m"
# query = "query-1"
# overprovisioning_factor = 1.1
# prometheus_address = "34.65.62.83:9090"
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
            "http://" + prometheus_address + "/api/v1/query?query=sum(rate(kafka_server_brokertopicmetrics_messagesin_total[1m])) by (topic)")
        true_processing = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=avg(flink_taskmanager_job_task_numRecordsOutPerSecond) by (task_name) / (avg(flink_taskmanager_job_task_busyTimeMsPerSecond) by (task_name) / 1000)")
        lag = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions) by (task_name)")

        latency = requests.get(
            "http://" + prometheus_address + "/api/v1/query?query=avg(flink_taskmanager_job_task_operator_currentEmitEventTimeLag) / 1000")
        latency_value = latency.json()["data"]["result"][0]["value"][1]
        print("latency value: " + str(latency_value))

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
        lag = extract_per_operator_metrics(lag)
        source_true_processing = extract_per_operator_metrics(true_processing)

        try:
            del input_rate_kafka["__consumer_offsets"]
        except:
            print("coudn't delete key")


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
            for key in input_rate_kafka.keys():
                row = [key, 0, 1, timestamp, 1, 1, 1, 1]
                writer.writerow(row)

            for key in input_rates_per_operator:
                formatted_key = key.split(" ")
                operator, operator_id = formatted_key[0], formatted_key[1]
                row = [operator, operator_id, int(processors_per_operator[operator]), timestamp, true_processing_rate[key], true_output_rate[key], input_rates_per_operator[key], output_rates_per_operator[key]]
                writer.writerow(row)
        print("Wrote rates file")

        operator_set = set()
        topology_order = []
        edges = {}
        with open('./ds2_query_data/flink_topology_' + query + '.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\n')
            for index, row in enumerate(reader):
                if index == 0:
                    continue
                row_values = row[0].split(",")
                if row_values[0] not in edges:
                    edges[row_values[0]] = [row_values[3]]
                else:
                    edges[row_values[0]].append(row_values[3])
                # if row_values[0] not in operator_set:
                #     topology_order.append(row_values[0])
                #     operator_set.add(row_values[0])
                # if row_values[3] not in operator_set:
                #     topology_order.append(row_values[3])
                #     operator_set.add(row_values[3])
        print(edges)

        lag_per_topic = {}
        source_to_topic={"Source:_BidsSource":"bids_topic", "Source:_auctionsSource":"auction_topic", "Source:_personSource":"person_topic", "Source:_BidsSource____Timestamps_Watermarks":"bids_topic"}
        for key, value in lag.items():
            lag_per_topic[source_to_topic[key]] = float(value) / lag_processing_time

        print("source rate")
        print(input_rate_kafka)
        print("extra rate due to lag")
        print(lag_per_topic)

        with open("ds2_query_data/" + query + "_source_rates.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["# source_operator_name","output_rate_per_instance (records/s)"]
            writer.writerow(header)
            for key, value in input_rate_kafka.items():
                row = [key, input_rate_kafka[key]]
                writer.writerow(row)
        print("Wrote source rate file")

        # setting number of operators for kafka topic to 1 so it can be used in topology.
        for key in input_rate_kafka.keys():
            processors_per_operator[key] = 1

        with open('./ds2_query_data/flink_topology_' + query + '2.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id1","operator_name1","total_number_of_operator_instances1","operator_id2","operator_name2","total_number_of_operator_instances2"]
            writer.writerow(header)
            for key in edges.keys():
                for edge in edges[key]:
                    row = [key, key, int(processors_per_operator[key]),edge, edge,int(processors_per_operator[edge])]
                    writer.writerow(row)
        print("Wrote topology file")

        ds2_model_result = subprocess.run(["cargo", "run", "--release", "--bin", "policy", "--", "--topo", "ds2_query_data/flink_topology_" + query + "2.csv", "--rates", "ds2_query_data/flink_rates_" + query + ".log", "--source-rates", "ds2_query_data/" + query + "_source_rates.csv", "--system", "flink"], capture_output=True)
        output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
        output_text_values = output_text.split(",")
        suggested_parallelism = {}

        filtered = []
        for val in output_text_values:
            if "topic" not in val:
                val = val.replace(" NodeIndex(0)\"", "")
                val = val.replace(" NodeIndex(4)\"", "")
                filtered.append(val)

        for i in range(0, len(filtered), 2):
            suggested_parallelism[filtered[i]] = filtered[i + 1].replace("\"", "")

        print("DS2 model result")
        print(suggested_parallelism)


        number_of_taskmanagers = 0
        for key, val in suggested_parallelism.items():
            number_of_taskmanagers = max(number_of_taskmanagers, int(val))

        print("Suggested number of taskmanagers", number_of_taskmanagers)

        number_of_taskmanagers = math.ceil(overprovisioning_factor * number_of_taskmanagers)

        print("Suggested number of taskmanagers after overporivisioning", number_of_taskmanagers)

        if number_of_taskmanagers > max_replicas:
            number_of_taskmanagers = 16
        if number_of_taskmanagers <= 0:
            number_of_taskmanagers = 1

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
            if current_number_of_taskmanagers != number_of_taskmanagers:
                if number_of_taskmanagers > current_number_of_taskmanagers and float(latency_value) > scale_up_lag_threshold:
                    print("scaling up to: ", number_of_taskmanagers)
                    new_number_of_taskmanagers = number_of_taskmanagers
                    body = {"spec": {"replicas": new_number_of_taskmanagers}}
                    api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
                if number_of_taskmanagers < current_number_of_taskmanagers and float(latency_value) < scale_down_lag_threshold:
                    print("scaling down to: ", number_of_taskmanagers)
                    new_number_of_taskmanagers = number_of_taskmanagers
                    body = {"spec": {"replicas": new_number_of_taskmanagers}}
                    api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default",
                                                                        body=body, pretty=True)
            else:
                print("no change in paralellism")
        else:
            print("in cooldown")

        time.sleep(sleep_time)


def keep_running():
    try:
        run()
    except:
        traceback.print_exc()
        time.sleep(10)
        keep_running()

keep_running()