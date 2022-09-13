#!/bin/bash
minikube start --memory 2200 --cpus 4 #8092 was set earlier

minikube addons enable metrics-server

kubectl apply -f flink-configuration-configmap.yaml
kubectl apply -f jobmanager-application.yaml
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f taskmanager-job-deployment.yaml

kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml

echo "starting kafka"

# start kafka
kubectl apply -f kafka-service.yaml
kubectl apply -f kafka-deployment.yaml

# kubectl apply -f ./dhalion/ds2-deployment.yaml
# kubectl apply -f ./dhalion/ds2-service.yaml
# kubectl apply -f ./dhalion/rbac_rules.yaml

# launch a container for running the data generator

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml


helm install grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json

# helm install my-release prometheus-community/prometheus-adapter

# helm install custom-pod-autoscaler-operator https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/v1.1.1/custom-pod-autoscaler-operator-v1.1.1.tgz

echo "Waiting for everything to be ready"

kubectl wait --timeout=5m --for=condition=available deployments --all
kubectl wait --timeout=5m --for=condition=ready pods --all

echo "deployment done"