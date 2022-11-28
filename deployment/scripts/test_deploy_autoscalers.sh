#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2-original, ds2-updated, HPA, varga1, varga2}
QUERY=$2
MODE=$3 #{reactive, non-reactive}
echo "Deploying autoscaler: $AUTOSCALER with query $QUERY on mode $MODE"
export METRIC=$METRIC
export QUERY=$QUERY

if [ "$MODE" == "reactive" ]
then
  export USE_FLINK_REACTIVE="true"
else
  export USE_FLINK_REACTIVE="false"
fi

kubectl apply -f ../yamls/autoscalers/autoscaler_rbac_rules.yaml
case $AUTOSCALER in
  "dhalion")
    envsubst < ../yamls/autoscalers/dhalion/deployment_dhalion.yaml | kubectl apply -f -
    ;;

  "hpa-cpu")
    envsubst < ../yamls/autoscalers/hpa/deployment_hpa_cpu.yaml | kubectl apply -f -
    ;;
  *)
esac



