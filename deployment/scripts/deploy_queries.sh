#!/bin/bash

QUERY=${1}                      # {1, 2, 3, 5, 8, 11}
MODE=${2}                       # {reactive, non-reactive}
INITIAL_PARALLELISM=${3}        # Parallelism of topology (per operator for non-reactive, #taskmanagers for reactive)
AVAILABLE_TASKMANAGERS=${4}     # Maximum available taskmanagers
LOAD_PATTERN=${5}               # {cosinus, cosinus-spikes, random, increase, decrease}
EXPERIMENT_DURATION=${6}
WORKLOAD_CONFIGURATION_0=${7}
WORKLOAD_CONFIGURATION_1=${8}
WORKLOAD_CONFIGURATION_2=${9}
WORKLOAD_CONFIGURATION_3=${10}

echo "Deploying query ${QUERY} with ${MODE} mode with the following parameters:
  INITIAL_PARALLELISM=${INITIAL_PARALLELISM}
  AVAILABLE_TASKMANAGERS=${AVAILABLE_TASKMANAGERS}
  LOAD_PATTERN=${LOAD_PATTERN}
  EXPERIMENT_DURATION=${EXPERIMENT_DURATION}
  WORKLOAD_CONFIGURATION_0=${WORKLOAD_CONFIGURATION_0}
  WORKLOAD_CONFIGURATION_1=${WORKLOAD_CONFIGURATION_1}
  WORKLOAD_CONFIGURATION_2=${WORKLOAD_CONFIGURATION_2}
  WORKLOAD_CONFIGURATION_3=${WORKLOAD_CONFIGURATION_3}
  "

# Deploy flink configuration
if [ "${MODE}" == "reactive" ]
then
  kubectl apply -f ../yamls/flink_basic/flink-configuration-configmap.yaml
else
  kubectl apply -f ../yamls/flink_basic/flink-configuration-configmap-non-reactive.yaml
fi
kubectl apply -f ../yamls/flink_basic/jobmanager-rest-service.yaml
kubectl apply -f ../yamls/flink_basic/jobmanager-service.yaml

# Deploy taskmanagers
if [ "${MODE}" == "reactive" ]
then
  TASKMANAGER_PARALLELISM="$INITIAL_PARALLELISM"
else
  if [ "${QUERY}" == "1" ] || [ "${QUERY}" == "2" ] || [ "${QUERY}" == "5" ] || [ "${QUERY}" == "11" ]
  then
    TASKMANAGER_PARALLELISM=$(("$INITIAL_PARALLELISM" * 3))
  elif [ "${QUERY}" == "8" ]
  then
    TASKMANAGER_PARALLELISM=$(("$INITIAL_PARALLELISM" * 4))
  elif [ "${QUERY}" == "3" ]
  then
    TASKMANAGER_PARALLELISM=$(("$INITIAL_PARALLELISM" * 5))
  else
    echo "Query ${QUERY} is not recognized. Failed setting TASKMANAGER_PARALLELISM."
  fi
fi
export TASKMANAGER_PARALLELISM=$TASKMANAGER_PARALLELISM
envsubst < ../yamls/flink_basic/experiments-taskmanager.yaml| kubectl apply -f -

# Deploy kafka
kubectl apply -f ../yamls/kafka/zookeeper-service.yaml
kubectl apply -f ../yamls/kafka/zookeeper-deployment.yaml
kubectl apply -f ../yamls/kafka/kafka-multi-broker.yaml

# Deploy prometheus
helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values ../yamls/monitoring/values-prometheus.yaml
kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus

kubectl wait --timeout=3m --for=condition=ready pods --all

# Deploy jobmanager
if [ "${MODE}" == "reactive" ]
then
  export QUERY=${QUERY}
  envsubst < ../yamls/queries/reactive/experiments-jobmanager-reactive.yaml| kubectl apply -f -
else
  export OPERATOR_PARALLELISM=${INITIAL_PARALLELISM}
  envsubst < ../yamls/queries/non-reactive/query"${QUERY}"-experiments-jobmanager-non-reactive.yaml | kubectl apply -f -
fi

# Wait for all pods to start
while kubectl get pods | grep -i 'ContainerCreating' > /dev/null;
do
    sleep 3
    echo "Waiting for pods to start..."
done

# Deploy workbench
export EXPERIMENT_DURATION=${EXPERIMENT_DURATION}
export WORKLOAD_CONFIGURATION_0=${WORKLOAD_CONFIGURATION_0}
export WORKLOAD_CONFIGURATION_1=${WORKLOAD_CONFIGURATION_1}
export WORKLOAD_CONFIGURATION_2=${WORKLOAD_CONFIGURATION_2}
export WORKLOAD_CONFIGURATION_3=${WORKLOAD_CONFIGURATION_3}
if [ "${QUERY}" == "3" ] || [ "${QUERY}" == "8" ]
then
  # For query 3 and 8: Generate auction and person stream
  kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions "$AVAILABLE_TASKMANAGERS" --topic auction_topic
  kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions "$AVAILABLE_TASKMANAGERS" --topic person_topic
  envsubst < ../yamls/workbench/auction-person-"${LOAD_PATTERN}"-workbench.yaml| kubectl apply -f -
else
  # For query 1, 2, 5, 11: Generate bids stream
  kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions "$AVAILABLE_TASKMANAGERS" --topic bids_topic
  envsubst < ../yamls/workbench/bid-"${LOAD_PATTERN}"-workbench.yaml| kubectl apply -f -
fi
