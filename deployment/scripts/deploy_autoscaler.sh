#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds-original, ds-updated, HPA, varga, varga_v2}
METRIC=$2
echo "autoscaler: $AUTOSCALER"
echo "Metric $METRIC"

#kubectl wait --timeout=4m --for=condition=ready statefulset --all

# dhalion
  kubectl apply -f dhalion_rbac_rules.yaml
  kubectl apply -f dhalion-deployment_v2.yaml

# ds2-original-reactive
  kubectl apply -f rules_ds2.yaml
  kubectl apply -f ds2-original-reactive.yaml

# ds2-updated-reactive
  kubectl apply -f rules_ds2.yaml
  kubectl apply -f ds2-updated-reactive.yaml

# HPA
  kubectl apply -f cpu-hpa-stabelized.yaml

# varga
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo update
  helm install my-release prometheus-community/prometheus-adapter
  kubectl delete deployment/my-release-prometheus-adapter
  kubectl apply -f prometheus-adapter-config.yaml
  kubectl apply -f adapter-deployment.yaml
#  kubectl wait --timeout=4m --for=condition=ready statefulset --all
  kubectl apply -f varga_HPA.yaml

# Varga_v2
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm repo update
  helm install my-release prometheus-community/prometheus-adapter
  kubectl delete deployment/my-release-prometheus-adapter
  kubectl apply -f prometheus-adapter-config_varga_v2.yaml
  kubectl apply -f adapter-deployment.yaml
#  kubectl wait --timeout=4m --for=condition=ready statefulset --all
  kubectl apply -f varga_HPA.yaml




