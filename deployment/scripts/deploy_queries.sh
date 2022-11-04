#!/bin/bash

QUERY=$1 #{1, 2, 3, 5, 8, 11}
MODE=$2 #{reactive, non-reactive}
echo "Deploying query $QUERY"

# common
if [$MODE = "reactive"]
then 
  kubectl apply -f flink-configuration-configmap.yaml
else
  kubectl apply -f flink-configuration-configmap-non-reactive.yaml
fi
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f experiments-taskmanager.yaml

kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml
kubectl apply -f kafka-multi-broker.yaml

helm install prometheus prometheus --repo https://prometheus-community.github.io/helm-charts --values values-prometheus.yaml
helm install grafana grafana --repo https://grafana.github.io/helm-charts --values values-grafana.yaml --set-file dashboards.default.flink-dashboard.json=grafana-dashboard.json --set-file dashboards.default.scaling-dashboard.json=grafana-dashboard-auto.json
kubectl expose deployment prometheus-server --type=LoadBalancer --name=my-external-prometheus
kubectl expose deployment grafana --type=LoadBalancer --name=my-external-grafana

kubectl wait --timeout=3m --for=condition=ready pods --all
#kubectl wait --timeout=2m --for=condition=ready statefulset --all

case $QUERY in
  1)
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
    if [$MODE = "reactive"]
    then
      kubectl apply -f query1-experiments-jobmanager.yaml
    else
      kubectl apply -f query1-experiments-jobmanager-non-reactive.yaml
    fi
    kubectl apply -f query1-workbench-deployment.yaml

  ;;
  2) # TODO: all the scripts for query 2
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
    if [$MODE = "reactive"]
    then
      kubectl apply -f query2-experiments-jobmanager.yaml
    else
      kubectl apply -f query2-experiments-jobmanager-non-reactive.yaml
    fi
    kubectl apply -f query2-workbench-deployment.yaml 

  ;;
  3)
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic auction_topic
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic person_topic
    if [$MODE = "reactive"]
    then
      kubectl apply -f query3-experiments-jobmanager.yaml
    else
      kubectl apply -f query3-experiments-jobmanager-non-reactive.yaml

    fi
    kubectl apply -f query3-workbench-deployment.yaml

  ;;
  5) # TODO: all the scripts for query 5
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
    if [$MODE = "reactive"]
    then
      kubectl apply -f query5-experiments-jobmanager.yaml
    else
      kubectl apply -f query5-experiments-jobmanager-non-reactive.yaml
    fi
    kubectl apply -f query5-workbench-deployment.yaml

  ;;
  8) # TODO: all the scripts for query 8
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
    if [$MODE = "reactive"]
    then
      kubectl apply -f query8-experiments-jobmanager.yaml
    else
      kubectl apply -f query8-experiments-jobmanager-non-reactive.yaml
    fi
    kubectl apply -f query8-workbench-deployment.yaml

  ;;
  11)
    kubectl exec kafka-2 -- /opt/kafka/bin/kafka-topics.sh --create -zookeeper zoo1:2181  --replication-factor 1 --partitions 24 --topic bids_topic
    if [$MODE = "reactive"]
    then
      kubectl apply -f query11-experiments-jobmanager.yaml
    else
      kubectl apply -f query11-experiments-jobmanager-non-reactive.yaml
    fi
    kubectl apply -f query11-workbench-deployment.yaml

  ;;
  *)
esac
