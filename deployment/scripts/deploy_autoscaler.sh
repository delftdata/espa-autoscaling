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
  *)
esac



