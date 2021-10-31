#!/bin/bash
minikube start --memory 8192 --cpus 4

minikube addons enable metrics-server



kubectl apply -f flink-configuration-configmap.yaml
kubectl apply -f jobmanager-application.yaml
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f taskmanager-job-deployment.yaml

kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml

# start kafka
kubectl apply -f kafka-service.yaml
kubectl apply -f kafka-deployment.yaml



# launch a container for running the data generator

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml


helm install grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json


echo "Waiting for everything to be ready"

  kubectl wait --timeout=5m --for=condition=available deployments --all
  kubectl wait --timeout=5m --for=condition=ready pods --all