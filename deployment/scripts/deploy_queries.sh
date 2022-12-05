#!/bin/bash

QUERY=$1                      #{1, 2, 3, 5, 8, 11}
MODE=$2                       #{reactive, non-reactive}
INPUT_RATE_MEAN=$3            # Mean of Cosinus pattern
INPUT_RATE_MAX_DIVERGENCE=$4  # Maximum divergence from Cosinus pattern
echo "Deploying query $QUERY with $MODE mode."

# Deploy flink
if [ "$MODE" == "reactive" ]
then 
  kubectl apply -f ../yamls/flink_basic/flink-configuration-configmap.yaml
else
  kubectl apply -f ../yamls/flink_basic/flink-configuration-configmap-non-reactive.yaml
fi
kubectl apply -f ../yamls/flink_basic/jobmanager-rest-service.yaml
kubectl apply -f ../yamls/flink_basic/jobmanager-service.yaml
kubectl apply -f ../yamls/flink_basic/experiments-taskmanager.yaml

# Deploy kafka
kubectl apply -f ../yamls/kafka/zookeeper-service.yaml
kubectl apply -f ../yamls/kafka/zookeeper-deployment.yaml
kubectl apply -f ../yamls/kafka/kafka-multi-broker.yaml

# Deploy prometheus
helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values ../yamls/monitoring/values-prometheus.yaml
helm install grafana grafana --repo https://grafana.github.io/helm-charts --values ../yamls/monitoring/values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=../yamls/monitoring/grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=../yamls/monitoring/grafana-dashboard-auto.json
kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus
kubectl expose deployment grafana --type=LoadBalancer --name=my-external-grafana

kubectl wait --timeout=3m --for=condition=ready pods --all

# Deploy jobmanager
if [ "$MODE" == "reactive" ]
then
  export QUERY=$QUERY
  envsubst < ../yamls/queries/reactive/experiments-jobmanager-reactive.yaml| kubectl apply -f -
else
  kubectl apply -f ../yamls/queries/non-reactive/query"${QUERY}"-experiments-jobmanager.yaml
fi

# Deploy workbench
export INPUT_RATE_MEAN=$INPUT_RATE_MEAN
export INPUT_RATE_MAX_DIVERGENCE=$INPUT_RATE_MAX_DIVERGENCE
if [ "$QUERY" == "3" ] || [ "$QUERY" == "8" ]
then
  kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic auction_topic
  kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic person_topic
  envsubst < ../yamls/queries/workbench/auction-person-workbench.yaml| kubectl apply -f -
else
  kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
  envsubst < ../yamls/queries/workbench/bid-workbench.yaml| kubectl apply -f -
fi
