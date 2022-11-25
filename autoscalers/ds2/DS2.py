import csv
import math
import os
import subprocess
import traceback
from pathlib import Path
import time
from timeit import default_timer as timer

from .DS2Configurations import DS2Configurations
from .DS2ApplicationManager import DS2ApplicationManager
from common import ScaleManager, Autoscaler


class DS2(Autoscaler):
    """
    DS2 autoscaler.
    """
    configurations: DS2Configurations
    applicationManager: DS2ApplicationManager
    scaleManager: ScaleManager

    operators: [str]
    topology: [(str, str)]
    topologyStatusFileName: str
    operatorRatesFileName: str
    kafkaSourceRatesFileName: str

    def __init__(self):
        """
        Constructor of DS2.
        """
        self.configurations = DS2Configurations()
        self.applicationManager = DS2ApplicationManager(self.configurations)
        self.scaleManager = ScaleManager(self.configurations, self.applicationManager)


    def setInitialMetrics(self):
        """
        Set initial metrics of autoscaler and create directories required for file writing.
        :return: None
        """
        self.operators = self.applicationManager.jobmanagerManager.getOperators()
        self.topology = self.applicationManager.gatherTopology(includeTopics=True)
        print(f"Found operators: '{self.operators}' with topology: '{self.topology}'")

        # Define file paths for passing through data with DS2 Rust code
        self.topologyStatusFileName = f"resources/tmp/ds2/data/flink_topology.csv"
        self.operatorRatesFileName = f"resources/tmp/ds2/data/flink_rates.log"
        self.kafkaSourceRatesFileName = f"resources/tmp/ds2/data/kafka_source_rates.csv"
        # Make directories of paths if they do not exist
        for path in [self.topologyStatusFileName, self.operatorRatesFileName, self.kafkaSourceRatesFileName]:
            directory = Path(path).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Added directory {directory}.")

    def writeOperatorRatesFile(self, topicKafkaInputRates: {str, int}, operatorParallelisms: {str, int},
                               subtaskTrueProcessingRates: {str, float}, subtaskTrueOutputRates: {str, int},
                               subtaskInputRates: {str, int}, subtaskOutputRates: {str, int}):
        """
        Write alll operator status' to file self.operatorRatesFileName.
        :param topicKafkaInputRates: Per topic kafka input rates with the topic as key and the input rates as value.
        :param operatorParallelisms: Per operator parallelism with the operatorName as key and the parallelism as value.
        :param subtaskTrueProcessingRates: Per subtask true processing rate: {"operator subtask_id", trueProcessingRate}
        :param subtaskTrueOutputRates: Per subtask true processing rate: {"operator subtask_id", trueProcessingRate}
        :param subtaskInputRates: Per subtask input rate: {"operator subtask_id", inputRate}
        :param subtaskOutputRates: Per subtask output rate: {"operator subtask_id",  outputRate}
        :return: None
        """
        with open(self.operatorRatesFileName, 'w+', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id", "operator_instance_id", "total_number_of_operator_instances", "epoch_timestamp",
                      "true_processing_rate", "true_output_rate", "observed_processing_rate", "observed_output_rate"]

            writer.writerow(header)
            timestamp = time.time_ns()

            for operator in topicKafkaInputRates.keys():
                row = [operator, 0, 1, timestamp, 1, 1, 1, 1]
                writer.writerow(row)

            for subtask in subtaskInputRates:
                try:
                    row = []
                    formatted_key = subtask.split(" ")
                    if len(formatted_key) >= 2:
                        # 1. operator_id
                        operator = formatted_key[0]
                        row.append(operator)
                        # 2. operator_instance_id
                        row.append(formatted_key[1])
                    else:
                        print(f"Error: unable to split subtask '{subtask}' into an operator and operator_instance_id: "
                              f"{formatted_key}. Only assigning operator and setting operator_instance_id to 1")
                        # operator_id
                        operator = subtask
                        row.append(operator)
                        # operator_instance_id
                        row.append(0)

                    # 3. total_number_of_operator_instances
                    if operator in operatorParallelisms:
                        row.append(operatorParallelisms[operator])
                    else:
                        print(f"Error: could not find operator '{operator}' in "
                              f"operatorParallelisms '{operatorParallelisms}'")
                        row.append(1)

                    # 4. epoch_timestamp
                    row.append(timestamp)

                    # 5. subtask true_processing_rate
                    if subtask in subtaskTrueProcessingRates:
                        row.append(subtaskTrueProcessingRates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskTrueProcessingRates '{subtaskTrueProcessingRates}'")
                        row.append(1)

                    # 6. subtask true_output_rate
                    if subtask in subtaskTrueOutputRates:
                        row.append(subtaskTrueOutputRates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskTrueOutputRates {subtaskTrueOutputRates}'")
                        row.append(1)

                    # 7. subtask observed_processing_rate
                    if subtask in subtaskInputRates:
                        row.append(subtaskInputRates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskInputRates {subtaskInputRates}'")
                        row.append(1)

                    # 8 subtask observed_output_rate
                    if subtask in subtaskOutputRates:
                        row.append(subtaskOutputRates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskOutputRates {subtaskOutputRates}'")
                        row.append(1)

                    writer.writerow(row)
                except:
                    print(f"Error: writing metrics of operator '{operator}' failed. Stacktrace:")
                    traceback.print_exc()

    def writeKafkaSourceRatesFile(self, topicKafkaInputRates: {str, int}):
        """
        Wirte KafkaSourceRates file including the rates of all topics.
        Data is written to self.kafkaSourceRatesFileName
        :param topicKafkaInputRates: Metrics including the inputrates of Kafka
        :return: None.
        """
        # write rate files
        with open(self.kafkaSourceRatesFileName, 'w+', newline='') as f:
            writer = csv.writer(f)
            header = ["# source_operator_name", "output_rate_per_instance (records/s)"]
            writer.writerow(header)
            for key, value in topicKafkaInputRates.items():
                row = [key, value]
                writer.writerow(row)

    def writeTopologyStatusFile(self, operatorParallelisms: {str, int}, topology: [(str, str)],
                                topicKafkaInputRates: {str, int}):
        """
        Write topology to a file. The kafkaTopicInputRates are used to also include the kafka_topics as inputs to DS2.
        The topology should also include the topics.
        Topology status is written to self.topologyStatusFileName
        :param operatorParallelisms: Parallelisms of known operators
        :param topology: Topology including all operators
        :param topicKafkaInputRates: All kafkaTopic Input rates
        :return:
        """
        # setting number of operators for kafka topic to 1, so it can be used in topology.
        parallelisms = dict(operatorParallelisms)
        for key in topicKafkaInputRates.keys():
            parallelisms[key] = 1

        with open(self.topologyStatusFileName, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id1", "operator_name1", "total_number_of_operator_instances1", "operator_id2",
                      "operator_name2", "total_number_of_operator_instances2"]
            writer.writerow(header)
            for lOperator, rOperator in topology:
                if lOperator in parallelisms and rOperator in parallelisms:
                    lOperatorParallelism = int(parallelisms[lOperator])
                    rOperatorParallelism = int(parallelisms[rOperator])
                    row = [lOperator, lOperator, lOperatorParallelism,
                           rOperator, rOperator, rOperatorParallelism, ]
                    writer.writerow(row)
                else:
                    print(f"Error: lOperator: '{lOperator}' or rOperator '{rOperator}' not found in "
                          f"operatorParallelisms {operatorParallelisms}")

    def runAutoscalerIteration(self):
        """
        DS2 iteration does the following:
        1. Sleep INTERATION_PERIOD_SECONDS
        2. Fetch metrics from prometheus
        3. Write metrics to file
        4. Call DS2 subroutine
        5. Scale to desired parallelism
        :return: None
        """

        print('\nExecuting next DS2 Iteration')
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Fetching metrics
        print("\t1. Fetching metrics")
        topicKafkaInputRates: {str, int} = self.applicationManager.gatherTopicKafkaInputRates()
        operatorParallelisms: {str, int} = self.applicationManager\
            .fetchCurrentOperatorParallelismInformation(self.operators)
        subtaskInputRates: {str, int} = self.applicationManager.gatherSubtaskInputRates()
        subtaskOutputRates: {str, int} = self.applicationManager.gatherSubtaskOutputRates()
        subtaskTrueProcessingRates: {str, float} = self.applicationManager.gatherSubtaskTrueProcessingRates(
            subtaskInputRates=subtaskInputRates)
        subtaskTrueOutputRates: {str, int} = self.applicationManager.gatherSubtaskTrueOutputRates(
            subtaskOutputRates=subtaskOutputRates)

        # print(f"Found the following metrics: \n"
        #       f"\ttopicKafkaInputRates: {topicKafkaInputRates}\n"
        #       f"\toperatorParallelisms: {operatorParallelisms}\n"
        #       f"\tsubtaskInputRates: {subtaskInputRates}\n"
        #       f"\tsubtaskOutputRates: {subtaskOutputRates}\n"
        #       f"\tsubtaskTrueProcessingRates: {subtaskTrueProcessingRates}\n"
        #       f"\tsubtaskTrueOutputRates: {subtaskTrueOutputRates}"
        # )

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
        somethingWentWrong = False
        print("\t3b. DS2's scaling module took ", timer() - start_time, "s to determine desired parallelisms.")

        # Fetch DS2's desired parallelisms
        print("\t4a. Fetching DS2's desired parallelisms")
        output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
        print(f"\t4b. DS2 provided the following output: {output_text}")
        output_text_values = output_text.split(",")
        useful_output = []
        for val in output_text_values:
            if "topic" not in val:
                substringsToRemove = [" ", "NodeIndex", "(0)", "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)",
                                      "(9)", "\""]
                for substringToRemove in substringsToRemove:
                    val = val.replace(substringToRemove, "")
                useful_output.append(val)

        desiredParallelisms: {str, int} = {}
        for i in range(0, len(useful_output), 2):
            if len(useful_output) > i + 1:
                operator = useful_output[i]
                desiredParallelism = math.ceil(float(useful_output[i + 1]))
                desiredParallelism = min(desiredParallelism, self.configurations.MAX_PARALLELISM)
                desiredParallelism = max(desiredParallelism, self.configurations.MIN_PARALLELISM)
                desiredParallelisms[operator] = desiredParallelism
            else:
                print(f"Error: useful_output {useful_output} is not large enough to process the next desiredParallelism"
                      f" i={i}.")
                somethingWentWrong = True

        if somethingWentWrong:
            print(f"Getting DS2 prediction went wrong. It gave the following result:\n\n"
                  f"Output:\n{ds2_model_result.stdout}\n\n"
                  f"Errors:\n{ds2_model_result.stderr}\n\n"
                  f"Return code:\n{ds2_model_result.returncode}\n\n")

        print(f"\t5. Desired parallelisms: {desiredParallelisms}")

        # Scale to desired parallelisms
        self.scaleManager.performScaleOperations(operatorParallelisms, desiredParallelisms)
