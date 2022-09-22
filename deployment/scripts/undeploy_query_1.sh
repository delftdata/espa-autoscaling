#!/bin/bash

echo "Undeploying query 1"
kubectl delete --wait=true -f flink-configuration-configmap.yaml
kubectl delete --wait=true -f jobmanager-rest-service.yaml
kubectl delete --wait=true -f jobmanager-service.yaml
kubectl delete --wait=true -f experiments-taskmanager.yaml
kubectl delete --wait=true -f zookeeper-service.yaml
kubectl delete --wait=true -f zookeeper-deployment.yaml
kubectl delete --wait=true -f kafka-multi-broker.yaml

helm uninstall prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml
helm uninstall grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json
kubectl delete service my-external-prometheus
kubectl delete service my-external-grafana

kubectl wait --timeout=3m --for=condition=ready pods --all
kubectl wait --timeout=2m --for=condition=ready statefulset --all

kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic

kubectl delete --wait=true -f  query1-experiments-jobmanager.yaml
kubectl delete --wait=true -f  query1-workbench-deployment.yaml
echo "Finished undeploying query 1"



