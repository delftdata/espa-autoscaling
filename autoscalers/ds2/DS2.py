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
    application_manager: DS2ApplicationManager
    scale_manager: ScaleManager

    operators: [str]
    topology: [(str, str)]
    topology_status_file_name: str
    operator_rates_file_name: str
    kafka_source_rates_file_name: str

    def __init__(self):
        """
        Constructor of DS2.
        """
        self.configurations = DS2Configurations()
        self.application_manager = DS2ApplicationManager(self.configurations)
        self.scale_manager = ScaleManager(self.configurations, self.application_manager)


    def initialize(self):
        """
        Set initial metrics of autoscaler and create directories required for file writing.
        :return: None
        """
        self.application_manager.initialize()
        self.operators = self.application_manager.jobmanagerManager.getOperators()
        self.topology = self.application_manager.gather_topology(include_topics=True)
        print(f"Found operators: '{self.operators}' with topology: '{self.topology}'")

        # Define file paths for passing through data with DS2 Rust code
        self.topology_status_file_name = f"resources/tmp/ds2/data/flink_topology.csv"
        self.operator_rates_file_name = f"resources/tmp/ds2/data/flink_rates.log"
        self.kafka_source_rates_file_name = f"resources/tmp/ds2/data/kafka_source_rates.csv"
        # Make directories of paths if they do not exist
        for path in [self.topology_status_file_name, self.operator_rates_file_name, self.kafka_source_rates_file_name]:
            directory = Path(path).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Added directory {directory}.")

    def write_operator_rates_to_file(self, topic_kafka_input_rates: dict[str, int], operator_parallelisms: dict[str, int],
                                     subtask_true_processing_rates: dict[str, float], subtask_true_output_rates: dict[str, int],
                                     subtask_input_rates: dict[str, int], subtask_output_rates: dict[str, int]) -> bool:
        """
        Write alll operator status' to file self.operatorRatesFileName.
        :param topic_kafka_input_rates: Per topic kafka input rates with the topic as key and the input rates as value.
        :param operator_parallelisms: Per operator parallelism with the operatorName as key and the parallelism as value.
        :param subtask_true_processing_rates: Per subtask true processing rate: {"operator subtask_id", trueProcessingRate}
        :param subtask_true_output_rates: Per subtask true processing rate: {"operator subtask_id", trueProcessingRate}
        :param subtask_input_rates: Per subtask input rate: {"operator subtask_id", inputRate}
        :param subtask_output_rates: Per subtask output rate: {"operator subtask_id",  outputRate}
        :return: Boolean indicating whether something went wrong. False if nothing was wrong.
        """

        something_went_wrong = False

        with open(self.operator_rates_file_name, 'w+', newline='') as f:
            writer = csv.writer(f)
            header = ["# operator_id", "operator_instance_id", "total_number_of_operator_instances", "epoch_timestamp",
                      "true_processing_rate", "true_output_rate", "observed_processing_rate", "observed_output_rate"]

            writer.writerow(header)
            timestamp = time.time_ns()

            for operator in topic_kafka_input_rates.keys():
                row = [operator, 0, 1, timestamp, 1, 1, 1, 1]
                writer.writerow(row)

            if len(operator_parallelisms) > min(len(subtask_true_processing_rates), len(subtask_output_rates),
                                                len(subtask_input_rates), len(subtask_output_rates)):
                print("Error: subtask metrics contained less subtasks than operators in the topology.")
                something_went_wrong = True

            for subtask in subtask_input_rates:
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
                        something_went_wrong = True

                    # 3. total_number_of_operator_instances
                    if operator in operator_parallelisms:
                        row.append(operator_parallelisms[operator])
                    else:
                        print(f"Error: could not find operator '{operator}' in "
                              f"operatorParallelisms '{operator_parallelisms}'")
                        row.append(1)
                        something_went_wrong = True

                    # 4. epoch_timestamp
                    row.append(timestamp)

                    # 5. subtask true_processing_rate
                    if subtask in subtask_true_processing_rates:
                        row.append(subtask_true_processing_rates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskTrueProcessingRates '{subtask_true_processing_rates}'")
                        row.append(1)
                        something_went_wrong = True

                    # 6. subtask true_output_rate
                    if subtask in subtask_true_output_rates:
                        row.append(subtask_true_output_rates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskTrueOutputRates {subtask_true_output_rates}'")
                        row.append(1)
                        something_went_wrong = True

                    # 7. subtask observed_processing_rate
                    if subtask in subtask_input_rates:
                        row.append(subtask_input_rates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskInputRates {subtask_input_rates}'")
                        row.append(1)
                        something_went_wrong = True

                    # 8 subtask observed_output_rate
                    if subtask in subtask_output_rates:
                        row.append(subtask_output_rates[subtask])
                    else:
                        print(f"Error: could not find subtask '{subtask}' in "
                              f"subtaskOutputRates {subtask_output_rates}'")
                        row.append(1)
                        something_went_wrong = True

                    writer.writerow(row)
                except:
                    print(f"Error: writing metrics of operator '{operator}' failed. Stacktrace:")
                    traceback.print_exc()
                    something_went_wrong = True

            f.close()
        return not something_went_wrong

    def write_kafka_source_rates_to_file(self, topic_kafka_input_rates: dict[str, int]) -> bool:
        """
        Wirte KafkaSourceRates file including the rates of all topics.
        Data is written to self.kafkaSourceRatesFileName
        :param topic_kafka_input_rates: Metrics including the input-rates of Kafka
        :return: Boolean indicating whether something went wrong. False if nothing was wrong.
        """
        something_went_wrong = False
        # write rate files
        with open(self.kafka_source_rates_file_name, 'w+', newline='') as f:
            writer = csv.writer(f)
            header = ["# source_operator_name", "output_rate_per_instance (records/s)"]
            writer.writerow(header)
            for key, value in topic_kafka_input_rates.items():
                row = [key, value]
                writer.writerow(row)
            f.close()
        return not something_went_wrong

    def write_topology_status_to_file(self, operator_parallelisms: dict[str, int], topology: [(str, str)],
                                      topic_kafka_input_rates: dict[str, int]) -> bool:
        """
        Write topology to a file. The kafkaTopicInputRates are used to also include the kafka_topics as inputs to DS2.
        The topology should also include the topics.
        Topology status is written to self.topologyStatusFileName
        :param operator_parallelisms: Parallelisms of known operators
        :param topology: Topology including all operators
        :param topic_kafka_input_rates: All kafkaTopic Input rates
        :return: Boolean indicating whether writing went correctly.
        """
        something_went_wrong = False

        # setting number of operators for kafka topic to 1, so it can be used in topology.
        parallelisms = dict(operator_parallelisms)
        for key in topic_kafka_input_rates.keys():
            parallelisms[key] = 1

        with open(self.topology_status_file_name, 'w', newline='') as f:
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
                          f"operatorParallelisms {operator_parallelisms}")
                    something_went_wrong = True
            f.close()
        return not something_went_wrong

    def run_autoscaler_iteration(self):
        """
        DS2 iteration does the following:
        1. Sleep INTERATION_PERIOD_SECONDS
        2. Fetch metrics from prometheus
        3. Write metrics to file
        4. Call DS2 subroutine
        5. Scale to desired parallelism
        :return: None
        """

        print('Executing next DS2 Iteration')
        time.sleep(self.configurations.ITERATION_PERIOD_SECONDS)

        # Fetching metrics
        print("Fetching metrics")
        topic_kafka_input_rates: {str, int} = self.application_manager.gather_topic_kafka_input_rates()
        operator_parallelisms: {str, int} = self.application_manager.fetch_current_operator_parallelism_information(self.operators)
        subtask_input_rates: {str, int} = self.application_manager.gather_subtask_input_rates()
        subtask_output_rates: {str, int} = self.application_manager.gather_subtask_output_rates()

        subtask_busy_times = self.application_manager.gather_subtask_busy_times()
        subtask_true_processing_rates: {str, float} = self.application_manager.gather_subtask_true_processing_rates(
            subtask_busy_times=subtask_busy_times,
            subtask_input_rates=subtask_input_rates,
            maximum_busy_time=self.configurations.DS2_MAXIMUM_BUSY_TIME
        )
        subtask_true_output_rates: {str, int} = self.application_manager.gather_subtask_true_output_rates(
            subtask_busy_times=subtask_busy_times,
            subtask_output_rates=subtask_output_rates,
            maximum_busy_time=self.configurations.DS2_MAXIMUM_BUSY_TIME
        )

        self.application_manager.print_metrics({
            "topic_kafka_input_rates": topic_kafka_input_rates,
            "operator_parallelisms": operator_parallelisms,
            "subtask_input_rates": subtask_input_rates,
            "subtask_output_rates": subtask_output_rates,
            "subtask_busy_times": subtask_busy_times,
            "subtask_true_processing_rates": subtask_true_processing_rates,
            "subtask_true_output_rates": subtask_true_output_rates,
        })

        writing_succeeded = True
        # Writing metrics to file
        print("Writing metrics to file.")
        writing_succeeded = writing_succeeded and self.write_operator_rates_to_file(topic_kafka_input_rates=topic_kafka_input_rates,
                                                                                    operator_parallelisms=operator_parallelisms,
                                                                                    subtask_true_processing_rates=subtask_true_processing_rates,
                                                                                    subtask_true_output_rates=subtask_true_output_rates,
                                                                                    subtask_input_rates=subtask_input_rates,
                                                                                    subtask_output_rates=subtask_output_rates)

        writing_succeeded = writing_succeeded and self.write_kafka_source_rates_to_file(topic_kafka_input_rates=topic_kafka_input_rates)

        writing_succeeded = writing_succeeded and self.write_topology_status_to_file(operator_parallelisms=operator_parallelisms,
                                                                                     topology=self.topology,
                                                                                     topic_kafka_input_rates=topic_kafka_input_rates)

        # Call DS2 function
        if not writing_succeeded:
            print("Something went wrong while writing metrics to file. Skipping calling the ds2 iteration.")
        else:
            print("Calling DS2 scaling policy.")
            start_time = timer()
            ds2_model_result = subprocess.run([
                "cargo", "run", "--release", "--bin", "policy", "--",
                "--topo", self.topology_status_file_name,
                "--rates", self.operator_rates_file_name,
                "--source-rates", self.kafka_source_rates_file_name,
                "--system", "flink"
            ], capture_output=True)
            something_went_wrong = False
            print("DS2's scaling module took ", timer() - start_time, "s to determine desired parallelisms.")

            # Fetch DS2's desired parallelisms
            print("Fetching DS2's desired parallelisms")
            output_text = ds2_model_result.stdout.decode("utf-8").replace("\n", "")
            print(f"DS2 provided the following output: {output_text}")
            output_text_values = output_text.split(",")
            useful_output = []
            for val in output_text_values:
                if "topic" not in val:
                    substrings_to_remove = [" ", "NodeIndex", "(0)", "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)",
                                            "(9)", "\""]
                    for substring_to_remove in substrings_to_remove:
                        val = val.replace(substring_to_remove, "")
                    useful_output.append(val)

            desired_parallelisms: {str, int} = {}
            for i in range(0, len(useful_output), 2):
                if len(useful_output) > i + 1:
                    operator = useful_output[i]
                    desired_parallelism = math.ceil(float(useful_output[i + 1]))
                    desired_parallelism = max(desired_parallelism, 1)
                    desired_parallelisms[operator] = desired_parallelism
                else:
                    print(f"Error: useful_output {useful_output} is not large enough to process the next desiredParallelism"
                          f" i={i}.")
                    something_went_wrong = True

            if something_went_wrong:
                print(f"Getting DS2 prediction went wrong. It gave the following result:\n\n"
                      f"Output:\n{ds2_model_result.stdout}\n\n"
                      f"Errors:\n{ds2_model_result.stderr}\n\n"
                      f"Return code:\n{ds2_model_result.returncode}\n\n")

            print(f"\t5. Desired parallelisms: {desired_parallelisms}")

            # Scale to desired parallelisms
            self.scale_manager.perform_scale_operations(operator_parallelisms, desired_parallelisms)
