#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2-original, ds2-updated, HPA, varga1, varga2}
METRIC=$2
QUERY=$3
MODE=$4 #{reactive, non-reactive}
echo "Deploying autoscaler: $AUTOSCALER with metric $METRIC and query $QUERY"
export METRIC=$METRIC
export QUERY=$QUERY

#kubectl wait --timeout=4m --for=condition=ready statefulset --all

case $AUTOSCALER in
  "dhalion")
    kubectl apply -f ../yamls/autoscalers/dhalion/dhalion_rbac_rules.yaml
    envsubst < ../yamls/autoscalers/dhalion/dhalion-deployment_v2.yaml | kubectl apply -f -
    ;;
  "ds2-original")
    kubectl apply -f ../yamls/autoscalers/ds2/rules_ds2.yaml
    envsubst < ../yamls/autoscalers/ds2/ds2-original-"$MODE".yaml | kubectl apply -f -
    ;;
  "ds2-updated")
    kubectl apply -f ../yamls/autoscalers/ds2/rules_ds2.yaml
    envsubst < ../yamls/autoscalers/ds2/ds2-updated-"$MODE".yaml | kubectl apply -f -
    ;;
  "HPA")
    kubectl apply -f ../yamls/autoscalers/hpa/hpa-rbac-rules.yaml
    envsubst < ../yamls/autoscalers/hpa/hpa-cpu-"$MODE".yaml | kubectl apply -f -
    ;;
  "varga1")
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    helm install my-release prometheus-community/prometheus-adapter
    kubectl delete deployment/my-release-prometheus-adapter
    kubectl apply -f ../yamls/monitoring/prometheus-adapter-config.yaml
    kubectl apply -f ../yamls/monitoring/adapter-deployment.yaml
    #  kubectl wait --timeout=4m --for=condition=ready statefulset --all
    envsubst < ../yamls/autoscalers/varga/varga_HPA.yaml | kubectl apply -f -
    ;;
  "varga2")
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    helm install my-release prometheus-community/prometheus-adapter
    kubectl delete deployment/my-release-prometheus-adapter
    kubectl apply -f ../yamls/monitoring/prometheus-adapter-config_varga_v2.yaml
    kubectl apply -f ../yamls/monitoring/adapter-deployment.yaml
    #  kubectl wait --timeout=4m --for=condition=ready statefulset --all
    envsubst < ../yamls/autoscalers/varga/varga_HPA.yaml | kubectl apply -f -
    ;;
  *)
esac



