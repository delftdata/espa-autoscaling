import requests
import json
import math
import time
import csv
import subprocess
import os
from kubernetes import client, config, utils


# yaml template for jobmanager
def writeConfig(**kwargs):
    template = """apiVersion: batch/v1
kind: Job
metadata:
  name: flink-jobmanager
spec:
  template:
    metadata:
      annotations:
        prometheus.io/port: '9249'
        ververica.com/scrape_every_2s: 'true'
      labels:
        app: flink
        component: jobmanager
    spec:
      restartPolicy: OnFailure
      containers:
        - name: jobmanager
          image: {container}
          imagePullPolicy: Always
          env:
          args: {args}
          ports:
            - containerPort: 6123
              name: rpc
            - containerPort: 6124
              name: blob-server
            - containerPort: 8081
              name: webui
          livenessProbe:
            tcpSocket:
              port: 6123
            initialDelaySeconds: 30
            periodSeconds: 60
          volumeMounts:
            - name: flink-config-volume
              mountPath: /opt/flink/conf
            - name: savepoint-volume
              mountPath: /opt/flink/savepoints
          securityContext:
            runAsUser: 0  # refers to user _flink_ from official flink image, change if necessary
      volumes:
        - name: flink-config-volume
          configMap:
            name: flink-config
            items:
              - key: flink-conf.yaml
                path: flink-conf.yaml
              - key: log4j-console.properties
                path: log4j-console.properties
        - name: savepoint-volume
          hostPath:
            # directory location on host
            path: /host_mnt/c/temp/soccerdb-pv
            type: DirectoryOrCreate """

    with open('jobmanager_from_savepoint.yaml', 'w') as yfile:
        yfile.write(template.format(**kwargs))

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

cooldown = int(os.environ['COOLDOWN'])
avg_over_time = os.environ['AVG_OVER_TIME']
min_replicas = int(os.environ['MIN_REPLICAS'])
max_replicas = int(os.environ['MAX_REPLICAS'])
sleep_time = int(os.environ['SLEEP_TIME'])
container = os.environ["CONTAINER"]
job = os.environ["JOB"]

while True:
    print('Executing DS2 Script')

    input_rate_query = requests.get(
        "http://prometheus-server/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsInPerSecond[" + avg_over_time + "])")
    output_rate_query = requests.get(
        "http://prometheus-server/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsOutPerSecond[" + avg_over_time + "])")
    busy_time_query = requests.get(
        "http://prometheus-server/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond[" + avg_over_time + "])")
    number_of_processors_per_task = requests.get(
        "http://prometheus-server/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")

    input_rates_per_operator = extract_per_operator_metrics(input_rate_query, include_subtask=True)
    output_rates_per_operator = extract_per_operator_metrics(output_rate_query, include_subtask=True)
    busy_time_per_operator = extract_per_operator_metrics(busy_time_query, include_subtask=True)
    processors_per_operator = extract_per_operator_metrics(number_of_processors_per_task)
    operators = list(processors_per_operator.keys())

    print("Obtained metrics")

    true_processing_rate = {}
    for key in input_rates_per_operator:
        true_processing_rate[key] = input_rates_per_operator[key] / (busy_time_per_operator[key] / 1000)

    true_output_rate = {}
    for key in output_rates_per_operator:
        true_output_rate[key] = output_rates_per_operator[key] / (busy_time_per_operator[key] / 1000)

    with open('./examples/demo/flink_rates.log', 'w', newline='') as f:
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
    with open('./examples/demo/flink_topology.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
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


    with open('./examples/demo/flink_topology2.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["# operator_id1","operator_name1","total_number_of_operator_instances1","operator_id2","operator_name2","total_number_of_operator_instances2"]
        writer.writerow(header)
        for i in range(0, len(topology_order) - 1):
            row = [topology_order[i], topology_order[i], int(processors_per_operator[topology_order[i]]), topology_order[i + 1], topology_order[i + 1], int(processors_per_operator[topology_order[i + 1]])]
            writer.writerow(row)
    print("Wrote topology file")

    ds2_model_result = subprocess.run(["cargo", "run", "--release", "--bin", "policy", "--", "--topo", "examples/demo/flink_topology2.csv", "--rates", "examples/demo/flink_rates.log", "--system", "flink"], capture_output=True)
    output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
    output_text_values = output_text.split(",")
    suggested_parallelism = {}

    for i in range(0, len(output_text_values), 2):
        suggested_parallelism[output_text_values[i]] = output_text_values[i + 1]

    print("DS2 model result")
    print(suggested_parallelism)
    job_id_json = requests.get("http://flink-jobmanager-rest/jobs/")
    job_id = job_id_json.json()['jobs'][0]['id']

    savepoint = requests.post("http://flink-jobmanager-rest/jobs/" + job_id + "/savepoints")

    #sleep so savepoint can be taken
    time.sleep(5)
    trigger_id = savepoint.json()['request-id']
    savepoint_name = requests.get("http://flink-jobmanager-rest/jobs/" + job_id + "/savepoints/" + trigger_id)
    savepoint_path = savepoint_name.json()["operation"]["location"]

    stop_request = requests.post("http://flink-jobmanager-rest/jobs/" + job_id + "/stop")

    p1 = 1
    p2 = 2
    p3 = 1
    writeConfig(container=container,args =["standalone-job", "--job-classname", job, "--fromSavepoint", savepoint_path, "--topic", "topic", "--bootstrap.servers",
           "kafka-service:9092", "--group.id", "yolo", "--p1", p1, "--p2", p2, "--p3", p3])

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

    # scale taskmanager
    new_number_of_taskmanagers = 2
    body = {"spec": {"replicas": new_number_of_taskmanagers}}
    api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
    v1 = client.BatchV1Api

    # delete old jobmanager
    api_response = v1.delete_namespaced_job(name="flink-jobmanager", namespace="default", pretty=True)

    time.sleep(10)

    # deploy new job file with updated parrelalism
    k8s_client = client.ApiClient()
    yaml_file = "jobmanager_from_savepoint.yaml"
    utils.create_from_yaml(k8s_client, yaml_file)

    break