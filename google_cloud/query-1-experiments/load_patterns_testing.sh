#!/bin/bash

cd ..
cd common-files


kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml
kubectl apply -f kafka-multi-broker.yaml

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml

helm install grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json

kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus
kubectl expose deployment grafana --type=LoadBalancer --name=my-external-grafana

kubectl wait --timeout=3m --for=condition=ready pods --all

kubectl wait --timeout=3m --for=condition=ready statefulset --all

kubectl exec kafka-1 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic

# kubectl expose job flink-jobmanager
cd ..
cd query-1-experiments
kubectl apply -f workbench-deployment.yaml