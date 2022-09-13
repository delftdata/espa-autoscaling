#!/bin/bash

# Setup containers
bash deploy.sh

# Forward applications to ports
  # When run in WSL
  bash port_forwards_WSL.sh
  # TODO: run in default ubuntu

# Create Ubuntu to run PASAF
kubectl run workbench --image ubuntu -- sleep infinity

# Wait for all PODS to be ready
echo "Waiting for everything to be ready"
  kubectl wait --timeout=5m --for=condition=ready pods --all

# Now it is time to run our experiments

#########################
# EXPERIMENT CONFIGURATIONS
#########################

# DEMO_COS DEMO_SQUARE DEMO_CONSTANT EXPERIMENT_DEFAULT EXPERIMENT_SPECIALISED
DATASET_RUN=EXPERIMENT_SPECIALISED

##########################
# Run experiments
##########################

# Setup PASAF on workbench
kubectl exec workbench -- bash -c "
  apt update &&
  apt install -y maven git htop iputils-ping wget net-tools &&
  git clone https://github.com/WybeKoper/PASAF.git
"

# Install reactive-mode-demo-jobs
kubectl exec workbench -- bash -c "cd PASAF/reactive-mode-demo-jobs && mvn clean install"
# Install experiment jobs
kubectl exec workbench -- bash -c "cd PASAF/experiments && mvn clean install"

# Run
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

