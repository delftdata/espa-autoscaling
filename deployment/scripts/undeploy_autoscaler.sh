#!/bin/bash

# dhalion
  kubectl delete --wait=true -f dhalion_rbac_rules.yaml
  kubectl delete --wait=true -f dhalion-deployment_v2.yaml

# ds2-original-reactive
  kubectl delete --wait=true -f rules_ds2.yaml
  kubectl delete --wait=true -f ds2-original-reactive.yaml

# ds2-updated-reactive
  kubectl delete --wait=true -f rules_ds2.yaml
  kubectl delete --wait=true -f ds2-updated-reactive.yaml
# HPA
  kubectl delete --wait=true -f cpu-hpa-stabelized.yaml

# varga
  helm repo remove prometheus-community https://prometheus-community.github.io/helm-charts
  helm uninstall my-release prometheus-community/prometheus-adapter
  kubectl delete --wait=true -f prometheus-adapter-config.yaml
  kubectl delete --wait=true -f adapter-deployment.yaml
  kubectl delete --wait=true -f varga_HPA.yaml

# Varge_v2
  helm repo remove prometheus-community https://prometheus-community.github.io/helm-charts
  helm uninstall my-release prometheus-community/prometheus-adapter
  kubectl delete --wait=true -f prometheus-adapter-config_varga_v2.yaml
  kubectl delete --wait=true -f adapter-deployment.yaml
  kubectl delete --wait=true -f varga_HPA.yaml



