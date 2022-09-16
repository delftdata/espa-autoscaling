#!/bin/bash

# DEMO_COS DEMO_SQUARE DEMO_CONSTANT EXPERIMENT_DEFAULT EXPERIMENT_SPECIALISED
DATASET_RUN=EXPERIMENT_DEFAULT

echo "Running experiment: ${DATASET_RUN}"
echo "Warning: Workbench pod should be deployed beforehand!"

case $DATASET_RUN in
  DEMO_COS)
      # Run reactive-mode-demo-jobs - cos
      kubectl exec workbench -- bash -c "cd PASAF/reactive-mode-demo-jobs && mvn exec:java -Dexec.mainClass='org.apache.flink.DataGen' -Dexec.args='topic 1 kafka-service:9092 cos false 8 15 50000'"
    ;;
  DEMO_SQUARE)
      # Run reactive-mode-demo-jobs - square
      kubectl exec workbench -- bash -c "cd PASAF/reactive-mode-demo-jobs && mvn exec:java -Dexec.mainClass='org.apache.flink.DataGen' -Dexec.args='topic 1 kafka-service:9092 square false 8 60 10000'"
    ;;
  DEMO_CONSTANT)
      # Run reactive-mode-demo-jobs - constant
      kubectl exec workbench -- bash -c "cd PASAF/reactive-mode-demo-jobs && mvn exec:java -Dexec.mainClass='org.apache.flink.DataGen' -Dexec.args='topic 1 kafka-service:9092 constant false 8 30 10000'"
    ;;
  EXPERIMENT_DEFAULT)
      # Run experiments with default parameters
      kubectl exec workbench -- bash -c "cd PASAF/experiments && mvn exec:java -Dexec.mainClass='ch.ethz.systems.strymon.ds2.flink.nexmark.sources.BidSourceFunctionGeneratorKafka'"
    ;;
  EXPERIMENT_SPECIALISED)
      # Run experiments with specified parameters
      kubectl exec workbench -- bash -c "cd PASAF/experiments && mvn exec:java -Dexec.mainClass='ch.ethz.systems.strymon.ds2.flink.nexmark.sources.BidSourceFunctionGeneratorKafka' -Dexec.args='-p-source 4 --p-map 4'"
    ;;
esac

echo "Finished running experiment: ${DATASET_RUN}"