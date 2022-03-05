#!/bin/bash

kubectl apply -f ./common-files/flink-configuration-configmap.yaml
kubectl apply -f ./common-files/experiments-jobmanager.yaml
kubectl apply -f ./common-files/jobmanager-rest-service.yaml
kubectl apply -f ./common-files/jobmanager-service.yaml
kubectl apply -f ./common-files/experiments-taskmanager.yaml


kubectl apply -f ./common-files/zookeeper-service.yaml
kubectl apply -f ./common-files/zookeeper-deployment.yaml
kubectl apply -f ./common-files/kafka-multi-broker.yaml

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values ./common-files/values-prometheus.yaml

helm install grafana grafana --repo https://grafana.github.io/helm-charts --values ./common-files/values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=./common-files/grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=./common-files/grafana-dashboard-auto.json

kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus
kubectl expose deployment grafana --type=LoadBalancer --name=my-external-grafana

kubectl wait --timeout=3m --for=condition=ready pods --all

kubectl wait --timeout=1m --for=condition=ready statefulset --all

kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic auction_topic
kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic person_topic

# kubectl expose job flink-jobmanager  

kubectl apply -f workbench-deployment.yaml
