import csv
import math
import os
import subprocess
import traceback
from pathlib import Path


from .DS2Configurations import DS2Configurations
from .Ds2MetricsGatherer import DS2MetricsGatherer
from common import ScaleManager, Autoscaler
from kubernetes import client, config
import time
from timeit import default_timer as timer


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
            - name: my-pvc-nfs
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
        - name: my-pvc-nfs
          persistentVolumeClaim:
            claimName: nfs """

    with open('jobmanager_from_savepoint.yaml', 'w') as yfile:
        yfile.write(template.format(**kwargs))



SAVEPOINT_IN_PROGRESS_STATUS = "IN_PROGRESS"
SAVEPOINT_COMPLETED_STATUS = "COMPLETED"


class DS2(Autoscaler):
    configurations: DS2Configurations
    metricsGatherer: DS2MetricsGatherer
    scaleManager: ScaleManager

    operators: [str]
    topology: [(str, str)]
    topologyStatusFileName: str
    operatorRatesFileName: str
    kafkaSourceRatesFileName: str

    def __init__(self):
        self.configurations = DS2Configurations()
        self.metricsGatherer = DS2MetricsGatherer(self.configurations)
        self.scaleManager = ScaleManager(self.configurations)
        if self.configurations.USE_FLINK_REACTIVE:
            config.load_incluster_config()
            v1 = client.AppsV1Api()
            self.metricsGatherer.v1 = v1
            self.scaleManager.v1 = v1

    def setInitialMetrics(self):
        self.operators = self.metricsGatherer.jobmanagerMetricGatherer.getOperators()
        self.topology = self.metricsGatherer.jobmanagerMetricGatherer.getTopology()
        print(f"Found operators: '{self.operators}' with topology: '{self.topology}'")

        # Define file paths for passing through data with DS2 Rust code
        self.topologyStatusFileName = f"resources/ds2/flink_topology.csv"
        self.operatorRatesFileName = f"resources/ds2/flink_rates.log"
        self.kafkaSourceRatesFileName = f"resources/ds2/kafka_source_rates.csv"
        # Make directories of paths if they do not exist
        for path in [self.topologyStatusFileName, self.operatorRatesFileName, self.kafkaSourceRatesFileName]:
            directory = Path(path).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Added directory {directory}.")

    def writeOperatorRatesFile(
            self,
            topicKafkaInputRates: {str, int},
            operatorParallelisms: {str, int},
            subtaskTrueProcessingRates: {str, float},
            subtaskTrueOutputRates: {str, int},
            subtaskInputRates: {str, int},
            subtaskOutputRates: {str, int},
    ):
        with open(self.operatorRatesFileName, 'w+', newline='') as f:
            writer = csv.writer(f)
            header = [
                "# operator_id",
                "operator_instance_id",
                "total_number_of_operator_instances",
                "epoch_timestamp",
                "true_processing_rate",
                "true_output_rate",
                "observed_processing_rate",
                "observed_output_rate"
            ]

            writer.writerow(header)

            timestamp = time.time_ns()
            for operator in topicKafkaInputRates.keys():
                row = [
                    operator,
                    0,
                    1,
                    timestamp,
                    1,
                    1,
                    1,
                    1
                ]
                writer.writerow(row)



            for subtask in subtaskInputRates:
                try:
                    row = []
                    formatted_key = subtask.split(" ")

                    # 1. operator_id
                    operator = formatted_key[0]
                    row.append(operator)
                    # 2. operator_instance_id
                    subtask_id = formatted_key[1]
                    row.append(subtask)

                    # 3. total_number_of_operator_instances
                    operatorParallelism = operatorParallelisms[operator]
                    row.append(operatorParallelism)

                    # 4. epoch_timestamp
                    row.append(timestamp)

                    # 5. true_processing_rate
                    subtaskTrueProcessingRate = subtaskTrueProcessingRates[subtask]
                    row.append(subtaskTrueProcessingRate)

                    # 6. true_output_rate
                    subtaskTrueOutputRate = subtaskTrueOutputRates[subtask]
                    row.append(subtaskTrueOutputRate)

                    # 7. observed_processing_rate
                    subtaskInputRate = subtaskInputRates[subtask]
                    row.append(subtaskInputRate)

                    # 8 observed_output_rate
                    subtaskOutputRate = subtaskOutputRates[subtask]
                    row.append(subtaskOutputRate)

                    writer.writerow(row)
                except:
                    print(f"Error: writing metrics of operator '{operator}' failed. Stacktrace:")
                    traceback.print_exc()

    def writeKafkaSourceRatesFile(self, topicKafkaInputRates: {str, int}):
        # write rate files
        with open(self.kafkaSourceRatesFileName, 'w+', newline='') as f:
            writer = csv.writer(f)
            header = ["# source_operator_name", "output_rate_per_instance (records/s)"]
            writer.writerow(header)
            for key, value in topicKafkaInputRates.items():
                row = [key, topicKafkaInputRates[key]]
                writer.writerow(row)
        print("Wrote source rate file")

    def writeTopologyStatusFile(self,
                                operatorParallelisms: {str, int},
                                topology: [(str, str)],
                                topicKafkaInputRates: {str, int}
                                ):
        # setting number of operators for kafka topic to 1, so it can be used in topology.
        for key in topicKafkaInputRates.keys():
            operatorParallelisms[key] = 1

        with open(self.topologyStatusFileName, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id1", "operator_name1", "total_number_of_operator_instances1", "operator_id2",
                      "operator_name2", "total_number_of_operator_instances2"]
            writer.writerow(header)
            for lOperator, rOperator in topology:
                lOperatorParallelism = int(operatorParallelisms[lOperator])
                rOperatorParallelism = int(operatorParallelisms[rOperator])
                row = [lOperator, lOperator, lOperatorParallelism,
                       rOperator, rOperator, rOperatorParallelism, ]
                writer.writerow(row)
        print("Wrote topology file")

    def runAutoscalerIteration(self):
        print('Executing DS2 Iteration')
        # Fetching metrics
        print("\t1. Fetching metrics")
        topicKafkaInputRates: {str, int} = self.metricsGatherer.gatherTopicKafkaInputRates()
        operatorParallelisms: {str, int} = self.metricsGatherer.fetchCurrentOperatorParallelismInformation()
        subtaskInputRates: {str, int} = self.metricsGatherer.gatherSubtaskInputRates()
        subtaskOutputRates: {str, int} = self.metricsGatherer.gatherSubtaskOutputRates()
        subtaskTrueProcessingRates: {str, float} = self.metricsGatherer.gatherSubtaskTrueProcessingRates(
            subtaskInputRates=subtaskInputRates)
        subtaskTrueOutputRates: {str, int} = self.metricsGatherer.gatherSubtaskTrueOutputRates(
            subtaskOutputRates=subtaskOutputRates)

        # Writing metrics to file
        print("\t2. Writing metrics to file")
        self.writeOperatorRatesFile(
            topicKafkaInputRates=topicKafkaInputRates,
            operatorParallelisms=operatorParallelisms,
            subtaskTrueProcessingRates=subtaskTrueProcessingRates,
            subtaskTrueOutputRates=subtaskTrueOutputRates,
            subtaskInputRates=subtaskInputRates,
            subtaskOutputRates=subtaskOutputRates,
        )

        self.writeKafkaSourceRatesFile(
            topicKafkaInputRates=topicKafkaInputRates
        )

        self.writeTopologyStatusFile(
            operatorParallelisms=operatorParallelisms,
            topology=self.topology,
            topicKafkaInputRates=topicKafkaInputRates,
        )

        # Call DS2 function
        print("\t3a. Calling DS2 scaling policy.")
        start_time = timer()
        ds2_model_result = subprocess.run([
            "cargo", "run", "--release", "--bin", "policy", "--",
            "--topo", self.topologyStatusFileName,
            "--rates", self.operatorRatesFileName,
            "--source-rates", self.kafkaSourceRatesFileName,
            "--system", "flink"
        ], capture_output=True)
        print("\t3b. DS2's scaling module took ", timer() - start_time, "s to determine desired parallelisms.")

        # Fetch DS2's desired parallelisms
        print("\t4. Fetching DS2's desired parallelisms")
        output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
        output_text_values = output_text.split(",")
        useful_output = []
        for val in output_text_values:
            if "topic" not in val:
                val = val.replace(" NodeIndex(0)\"", "")
                val = val.replace(" NodeIndex(4)\"", "")
                useful_output.append(val)

        desiredParallelisms: {str, int} = {}
        for i in range(0, len(useful_output), 2):
            operator = useful_output[i]
            desiredParallelism = math.ceil(float(useful_output[i + 1]))
            desiredParallelism = min(desiredParallelism, self.configurations.MAX_PARALLELISM)
            desiredParallelism = max(desiredParallelism, self.configurations.MIN_PARALLELISM)
            desiredParallelisms[operator] = desiredParallelism

        print(f"\t5. Desired parallelisms: {desiredParallelisms}")

        # Scale to desired parallelisms
        self.scaleManager.performScaleOperations(operatorParallelisms, desiredParallelisms)
