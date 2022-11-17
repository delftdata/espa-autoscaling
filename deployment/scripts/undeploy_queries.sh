#!/bin/bash

QUERY=$1 #{1, 3, 11}
MODE=$2 #{reactive, non-reactive}
echo "Deploying query $QUERY"

# common
if [ "$MODE" == "reactive" ]
then
  kubectl delete --wait=true -f ../yamls/flink_basic/flink-configuration-configmap.yaml
else
  kubectl delete --wait=true -f ../yamls/flink_basic/flink-configuration-configmap-non-reactive.yaml
fi
kubectl delete --wait=true -f ../yamls/flink_basic/jobmanager-rest-service.yaml
kubectl delete --wait=true -f ../yamls/flink_basic/jobmanager-service.yaml
kubectl delete --wait=true -f ../yamls/flink_basic/experiments-taskmanager.yaml

kubectl delete --wait=true -f ../yamls/kafka/zookeeper-service.yaml
kubectl delete --wait=true -f ../yamls/kafka/zookeeper-deployment.yaml
kubectl delete --wait=true -f ../yamls/kafka/kafka-multi-broker.yaml

helm uninstall prometheus
helm uninstall grafana
kubectl delete service my-external-prometheus
kubectl delete service my-external-grafana

case $QUERY in
  1)
    if [ "$MODE" == "reactive" ]
    then
      kubectl delete --wait=true -f  ../yamls/queries/query1/query1-experiments-jobmanager.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query1/query1-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query1/query1-experiments-jobmanager.yaml --timeout=60s
    else
      kubectl delete --wait=true -f  ../yamls/queries/query1/query1-experiments-jobmanager-non-reactive.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query1/query1-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query1/query1-experiments-jobmanager-non-reactive.yaml --timeout=60s
    fi
  ;;
  2)
    if [ "$MODE" == "reactive" ]
    then
      kubectl delete --wait=true -f  ../yamls/queries/query2/query2-experiments-jobmanager.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query2/query2-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query2/query2-experiments-jobmanager.yaml --timeout=60s
    else
      kubectl delete --wait=true -f  ../yamls/queries/query2/query2-experiments-jobmanager-non-reactive.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query2/query2-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query2/query2-experiments-jobmanager-non-reactive.yaml --timeout=60s
    fi
  ;;
  3)
    if [ "$MODE" == "reactive" ]
    then
      kubectl delete --wait=true -f  ../yamls/queries/query3/query3-experiments-jobmanager.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query3/query3-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query3/query3-experiments-jobmanager.yaml --timeout=60s
    else
      kubectl delete --wait=true -f  ../yamls/queries/query3/query3-experiments-jobmanager-non-reactive.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query3/query3-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query3/query3-experiments-jobmanager-non-reactive.yaml --timeout=60s
    fi
  ;;
  5)
    if [ "$MODE" == "reactive" ]
    then
      kubectl delete --wait=true -f  ../yamls/queries/query5/query5-experiments-jobmanager.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query5/query5-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query5/query5-experiments-jobmanager.yaml --timeout=60s
    else
      kubectl delete --wait=true -f  ../yamls/queries/query5/query5-experiments-jobmanager-non-reactive.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query5/query5-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query5/query5-experiments-jobmanager-non-reactive.yaml --timeout=60s
    fi
  ;;
  8)
    if [ "$MODE" == "reactive" ]
    then
      kubectl delete --wait=true -f  ../yamls/queries/query8/query8-experiments-jobmanager.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query8/query8-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query8/query8-experiments-jobmanager.yaml --timeout=60s
    else
      kubectl delete --wait=true -f  ../yamls/queries/query8/query8-experiments-jobmanager-non-reactive.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query8/query8-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query8/query8-experiments-jobmanager-non-reactive.yaml --timeout=60s
    fi
  ;;
  11)
    if [ "$MODE" == "reactive" ]
    then
      kubectl delete --wait=true -f  ../yamls/queries/query11/query11-experiments-jobmanager.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query11/query11-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query11/query11-experiments-jobmanager.yaml --timeout=60s
    else
      kubectl delete --wait=true -f  ../yamls/queries/query11/query11-experiments-jobmanager-non-reactive.yaml
      kubectl delete --wait=true -f  ../yamls/queries/query11/query11-workbench-deployment.yaml
      # Ensure it does not mess up its entanglement with nfs
      kubectl wait --for=delete -f ../yamls/queries/query11/query11-experiments-jobmanager-non-reactive.yaml --timeout=60s
    fi
  ;;
  *)
esac

# Ensure it does not mess up its entanglement with nfs
kubectl wait --for=delete -f ../yamls/flink_basic/experiments-taskmanager.yaml --timeout=60s

