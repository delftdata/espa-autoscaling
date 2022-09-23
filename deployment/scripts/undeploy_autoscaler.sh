#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2-original, ds2-updated, HPA, varga1, varga2}
METRIC=$2
echo "Undeploying autoscaler: $AUTOSCALER with metric $METRIC"

#kubectl wait --timeout=4m --for=condition=ready statefulset --all

case $AUTOSCALER in
  "dhalion")
    kubectl delete --wait=true -f dhalion_rbac_rules.yaml
    kubectl delete --wait=true -f dhalion-deployment_v2.yaml
  ;;
  "ds2-original")
    kubectl delete --wait=true -f rules_ds2.yaml
    kubectl delete --wait=true -f ds2-original-reactive.yaml
  ;;
  "ds2-updated")
    kubectl delete --wait=true -f rules_ds2.yaml
    kubectl delete --wait=true -f ds2-updated-reactive.yaml
  ;;
  "HPA")
    kubectl delete --wait=true -f cpu-hpa-stabelized.yaml
  ;;
  "varga1")
    helm repo remove prometheus-community https://prometheus-community.github.io/helm-charts
    helm uninstall my-release prometheus-community/prometheus-adapter
    kubectl delete --wait=true -f prometheus-adapter-config.yaml
    kubectl delete --wait=true -f adapter-deployment.yaml
    kubectl delete --wait=true -f varga_HPA.yaml
  ;;
  "varga2")
    helm repo remove prometheus-community https://prometheus-community.github.io/helm-charts
    helm uninstall my-release prometheus-community/prometheus-adapter
    kubectl delete --wait=true -f prometheus-adapter-config_varga_v2.yaml
    kubectl delete --wait=true -f adapter-deployment.yaml
    kubectl delete --wait=true -f varga_HPA.yaml
  ;;
  *)
esac














# dhalion


# ds2-original-reactive


# ds2-updated-reactive

# HPA


# varga


# Varge_v2




