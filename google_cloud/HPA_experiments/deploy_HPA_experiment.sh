#!/bin/bash

kubectl apply -f flink-configuration-configmap.yaml
kubectl apply -f experiments-jobmanager.yaml
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f experiments-taskmanager.yaml


kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml

# kubectl apply -f kafka-service.yaml
# kubectl apply -f kafka-deployment.yaml
kubectl apply -f kafka-multi-broker.yaml

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml


helm install grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json

kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus
kubectl expose deployment grafana --type=LoadBalancer --name=my-external-grafana

kubectl wait --timeout=3m --for=condition=ready pods --all

kubectl wait --timeout=1m --for=condition=ready statefulset --all

# kubectl exec workbench -- bash -c "apt update && apt install -y maven git htop iputils-ping wget net-tools && git clone https://github.com/WybeKoper/PASAF.git && cd PASAF/experiments && mvn clean install"
kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic auction_topic
kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic person_topic

# kubectl expose job flink-jobmanager  

kubectl apply -f workbench-deployment.yaml
