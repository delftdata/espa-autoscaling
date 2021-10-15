#!/bin/bash

bash deploy.sh


start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_flink.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_kafka.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_prometheus.sh

start "C:\\Program Files\\Git\\git-bash.exe" bash port_forward_grafana.sh



kubectl exec workbench -- bash -c "apt update && apt install -y maven git htop nano iputils-ping wget net-tools && git clone https://github.com/rmetzger/flink-reactive-mode-k8s-demo.git && cd flink-reactive-mode-k8s-demo/reactive-mode-demo-jobs && mvn clean install && mvn exec:java -Dexec.mainClass=\"org.apache.flink.DataGen\" -Dexec.args=\"topic 1 kafka-service:9092 cos\""


