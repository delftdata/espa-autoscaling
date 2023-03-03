#!/bin/bash

QUERY=${1} #{1, 3, 11}
MODE=${2} #{reactive, non-reactive}
NAMESPACE=${3}

echo "Undeploying query ${QUERY} with mode ${MODE} in namespace ${NAMESPACE}"

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
   kubectl delete --wait=true -f ../yamls/workbench/auction-person-cosinus-workbench.yaml
else
  # For query 1, 2, 5, 11: Generate bids stream
  kubectl delete --wait=true -f ../yamls/workbench/bid-cosinus-workbench.yaml
fi

# Wait for all pods to be removed
echo "Waiting initial 30 seconds for taskmanagers to be removed"
sleep 30
MAX_WAIT_TIME=300
while kubectl get pods | grep -i 'Terminating' > /dev/null;
do
    SLEEP_TIME=5
    echo "Waiting for terminating pods to be removed (${MAX_WAIT_TIME}s left)..."
    sleep "$SLEEP_TIME"
    MAX_WAIT_TIME=$(("${MAX_WAIT_TIME}"-"${SLEEP_TIME}"))
    if [ "${MAX_WAIT_TIME}" -le 0 ]
    then
        echo "MAX_WAIT_TIME REACHED (${MAX_WAIT_TIME}). Force terminating remaining pods."
        kubectl delete --all pods --force --namespace="${NAMESPACE}"
        echo "WAITING FOR PROPER REMOVAL"
        sleep 60
        echo "CHECKING AGAIN WHETHER PODS ARE GONE"
    fi
done