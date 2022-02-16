#!/bin/bash

kubectl apply -f flink-configuration-configmap.yaml
kubectl apply -f experiments-jobmanager.yaml
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f experiments-taskmanager.yaml


kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml

kubectl apply -f kafka-service.yaml
kubectl apply -f kafka-deployment.yaml

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml


helm install grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json

kubectl run workbench --image=ubuntu:21.04 -- sleep infinity

kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus
kubectl expose deployment grafana --type=LoadBalancer --name=my-external-grafana

echo "Waiting for everything to be ready"
  kubectl wait --timeout=5m --for=condition=ready pods --all

kubectl exec workbench -- bash -c "apt update && apt install -y maven git htop iputils-ping wget net-tools && git clone https://github.com/WybeKoper/PASAF.git && cd PASAF/experiments && mvn clean install"

# kubectl expose job flink-jobmanager  
