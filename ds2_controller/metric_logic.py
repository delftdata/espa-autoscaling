import requests
import json
import math
import time
import csv
import subprocess

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

prometheus_ip = "34.65.63.211"

while True:
    print('Executing DS2 Script')

    avg_over_time = "1m"
    input_rate_query = requests.get(
        "http://" + prometheus_ip + ":9090/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsInPerSecond[1m])")
    output_rate_query = requests.get(
        "http://" + prometheus_ip + ":9090/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_numRecordsOutPerSecond[1m])")
    busy_time_query = requests.get(
        "http://" + prometheus_ip + ":9090/api/v1/query?query=avg_over_time(flink_taskmanager_job_task_busyTimeMsPerSecond[1m])")
    number_of_processors_per_task = requests.get(
        "http://" + prometheus_ip + ":9090/api/v1/query?query=count(flink_taskmanager_job_task_operator_numRecordsIn) by (task_name)")

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


    with open('./examples/demo/flink_rates_test.log', 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["# operator_id", "operator_instance_id", "total_number_of_operator_instances", "epoch_timestamp", "true_processing_rate", "true_output_rate", "observed_processing_rate", "observed_output_rate"]
        writer.writerow(header)

        timestamp = time.time_ns()
        for key in input_rates_per_operator:
            formatted_key = key.split(" ")
            operator, operator_id = formatted_key[0], formatted_key[1]
            row = [operator, operator_id, int(processors_per_operator[operator]), timestamp, true_processing_rate[key], true_output_rate[key], input_rates_per_operator[key], output_rates_per_operator[key]]
            writer.writerow(row)


    operator_set = set()
    topology_order = []
    topology_parallelism = {}
    with open('./examples/demo/flink_topology_query_1.csv', newline='') as csvfile:
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


    ds2_model_result = subprocess.run(["cargo", "run", "--release", "--bin", "policy", "--", "--topo", "examples/demo/flink_topology2.csv", "--rates", "examples/demo/flink_rates_test.log", "--system", "flink"], capture_output=True)
    output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
    output_text_values = output_text.split(",")
    suggested_parallelism = {}

    print(output_text)
    for i in range(0, len(output_text_values), 2):
        suggested_parallelism[output_text_values[i]] = output_text_values[i + 1]

    print(suggested_parallelism)
    # job_id_json = requests.get("http://localhost:8081/jobs/")
    # job_id = job_id_json.json()['jobs'][0]['id']

    # savepoint = requests.post("http://localhost:8081/jobs/" + job_id + "/savepoints")

    # #sleep so savepoint can be taken
    # time.sleep(5)
    # trigger_id = savepoint.json()['request-id']
    # savepoint_name = requests.get("http://localhost:8081/jobs/" + job_id + "/savepoints/" + trigger_id)
    # savepoint_path = savepoint_name.json()["operation"]["location"]

    # print(job_id)
    # print(trigger_id)
    # print(savepoint_path)

    # # stop_request = requests.post("http://localhost:8081/jobs/" + job_id + "/stop")
    # # print(stop_request.text)
    # container = "9923/demo_custom_par:3"
    # job = "org.apache.flink.DemoJob"
    # p1 = 1
    # p2 = 2
    # p3 = 1
    # writeConfig(container=container,args =["standalone-job", "--job-classname", job, "--fromSavepoint", savepoint_path, "--topic", "topic", "--bootstrap.servers",
    #        "kafka-service:9092", "--group.id", "yolo", "--p1", p1, "--p2", p2, "--p3", p3])

    break