#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2-original, ds2-updated, HPA, varga1, varga2}
MODE=$2 #{reactive, non-reactive}
echo "Undeploying autoscaler: $AUTOSCALER"

#kubectl wait --timeout=4m --for=condition=ready statefulset --all

case $AUTOSCALER in
  "dhalion")
    kubectl delete --wait=true -f ../yamls/autoscalers/dhalion/dhalion_rbac_rules.yaml
    kubectl delete --wait=true -f ../yamls/autoscalers/dhalion/dhalion-deployment_v2.yaml
  ;;
  "ds2-original")
    kubectl delete --wait=true -f ../yamls/autoscalers/ds2/rules_ds2.yaml
    kubectl delete --wait=true -f ../yamls/autoscalers/ds2/ds2-original-"$MODE".yaml
  ;;
  "ds2-updated")
    kubectl delete --wait=true -f ../yamls/autoscalers/ds2/rules_ds2.yaml
    kubectl delete --wait=true -f ../yamls/autoscalers/ds2/ds2-updated-"$MODE".yaml
  ;;
  "HPA")
    kubectl delete --wait=true -f ../yamls/autoscalers/hpa/cpu-hpa-stabelized.yaml
  ;;
  "varga1")
    helm repo remove prometheus-community
    helm uninstall my-release
    kubectl delete --wait=true -f ../yamls/monitoring/prometheus-adapter-config.yaml
    kubectl delete --wait=true -f ../yamls/monitoring/adapter-deployment.yaml
    kubectl delete --wait=true -f ../yamls/autoscalers/varga/varga_HPA.yaml
  ;;
  "varga2")
    helm repo remove prometheus-community
    helm uninstall my-release
    kubectl delete --wait=true -f ../yamls/monitoring/prometheus-adapter-config_varga_v2.yaml
    kubectl delete --wait=true -f ../yamls/monitoring/adapter-deployment.yaml
    kubectl delete --wait=true -f ../yamls/autoscalers/varga/varga_HPA.yaml
  ;;
  *)
esac
