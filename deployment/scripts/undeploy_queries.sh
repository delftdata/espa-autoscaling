#!/bin/bash

QUERY=$1 #{1, 3, 11}
echo "Deploying query $QUERY"

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

case $QUERY in
  1)
    kubectl delete --wait=true -f  query1-experiments-jobmanager.yaml
    kubectl delete --wait=true -f  query1-workbench-deployment.yaml
  ;;
  3)
    kubectl delete --wait=true -f  query3-experiments-jobmanager.yaml
    kubectl delete --wait=true -f  query3-workbench-deployment.yaml
  ;;

  11)
    kubectl delete --wait=true -f  query11-experiments-jobmanager.yaml
    kubectl delete --wait=true -f  query11-workbench-deployment.yaml
  ;;
  *)
esac
