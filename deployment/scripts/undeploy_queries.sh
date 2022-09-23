#!/bin/bash

# common
kubectl delete --wait=true -f flink-configuration-configmap.yaml
kubectl delete --wait=true -f jobmanager-rest-service.yaml
kubectl delete --wait=true -f jobmanager-service.yaml
kubectl delete --wait=true -f experiments-taskmanager.yaml

kubectl delete --wait=true -f zookeeper-service.yaml
kubectl delete --wait=true -f zookeeper-deployment.yaml
kubectl delete --wait=true -f kafka-multi-broker.yaml

helm uninstall prometheus
helm uninstall grafana
kubectl delete service my-external-prometheus
kubectl delete service my-external-grafana

# Query 1
# kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
kubectl delete --wait=true -f  query1-experiments-jobmanager.yaml
kubectl delete --wait=true -f  query1-workbench-deployment.yaml

# Query 3
#kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic auction_topic
#kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic person_topic
kubectl delete --wait=true -f  query3-experiments-jobmanager.yaml
kubectl delete --wait=true -f  query3-workbench-deployment.yaml

# Query 11
#kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
kubectl delete --wait=true -f  query11-experiments-jobmanager.yaml
kubectl delete --wait=true -f  query11-workbench-deployment.yaml
