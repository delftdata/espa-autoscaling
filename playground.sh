#!/bin/bash

bash deploy.sh


start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_flink.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_kafka.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_prometheus.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_grafana.sh


kubectl run workbench --image=ubuntu:21.04 -- sleep infinity
echo "Waiting for everything to be ready"
  kubectl wait --timeout=5m --for=condition=ready pods --all

  
kubectl exec workbench -- bash -c "apt update && apt install -y maven git htop nano iputils-ping wget net-tools && git clone https://github.com/WybeKoper/PASAF.git && cd PASAF/reactive-mode-demo-jobs && mvn clean install"
# mvn exec:java -Dexec.mainClass="org.apache.flink.DataGen" -Dexec.args="topic 1 kafka-service:9092 cos false 8 15 50000"
# mvn exec:java -Dexec.mainClass="org.apache.flink.DataGen" -Dexec.args="topic 1 kafka-service:9092 square false 8 60"
# mvn exec:java -Dexec.mainClass="org.apache.flink.DataGen" -Dexec.args="topic 1 kafka-service:9092 constant false 8 30 10000"


