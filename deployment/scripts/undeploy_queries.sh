#!/bin/bash

QUERY=${1} #{1, 3, 11}
MODE=${2} #{reactive, non-reactive}
echo "Undeploying query ${QUERY} with mode ${MODE}"

# common
if [ "${MODE}" == "reactive" ]
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
kubectl delete service my-external-prometheus

# Undeploy jobmanager
if [ "${MODE}" == "reactive" ]
then
  kubectl delete --wait=true -f ../yamls/queries/reactive/experiments-jobmanager-reactive.yaml
else
  kubectl delete --wait=true -f ../yamls/queries/non-reactive/query"${QUERY}"-experiments-jobmanager-non-reactive.yaml
fi

# Undeploy workbench
if [ "${QUERY}" == "3" ] || [ "${QUERY}" == "8" ]
then
  # For query 3 and 8: Generate auction and person stream
   kubectl delete --wait=true -f ../yamls/queries/workbench/auction-person-workbench.yaml
else
  # For query 1, 2, 5, 11: Generate bids stream
  kubectl delete --wait=true -f ../yamls/queries/workbench/bid-workbench.yaml
fi

# Wait for all pods to be removed
while kubectl get pods | grep -i 'Terminating' > /dev/null;
do
    sleep 5
    echo "Waiting for terminating pods to be removed..."
done