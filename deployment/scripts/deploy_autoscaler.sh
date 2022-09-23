#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2-original, ds2-updated, HPA, varga1, varga2}
METRIC=$2
echo "Deploying autoscaler: $AUTOSCALER with metric $METRIC"
export METRIC=$METRIC

#kubectl wait --timeout=4m --for=condition=ready statefulset --all

case $AUTOSCALER in
  "dhalion")
    kubectl apply -f dhalion_rbac_rules.yaml
    envsubst < dhalion-deployment_v2.yaml | cat - && kubectl apply -f -
    ;;
  "ds2-original")
    kubectl apply -f rules_ds2.yaml
    envsubst < ds2-original-reactive.yaml | cat - && kubectl apply -f -
    ;;
  "ds2-updated")
    kubectl apply -f rules_ds2.yaml
    envsubst < ds2-updated-reactive.yaml | cat - && kubectl apply -f -
    ;;
  "HPA")
    envsubst < cpu-hpa-stabelized.yaml | cat - && kubectl apply -f -
    ;;
  "varga1")
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    helm install my-release prometheus-community/prometheus-adapter
    kubectl delete deployment/my-release-prometheus-adapter
    kubectl apply -f prometheus-adapter-config.yaml
    kubectl apply -f adapter-deployment.yaml
    #  kubectl wait --timeout=4m --for=condition=ready statefulset --all
    envsubst < varga_HPA.yaml | cat - && kubectl apply -f -
    ;;
  "varga2")
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    helm install my-release prometheus-community/prometheus-adapter
    kubectl delete deployment/my-release-prometheus-adapter
    kubectl apply -f prometheus-adapter-config_varga_v2.yaml
    kubectl apply -f adapter-deployment.yaml
    #  kubectl wait --timeout=4m --for=condition=ready statefulset --all
    envsubst < varga_HPA.yaml | cat - && kubectl apply -f -
    ;;
  *)
esac



