#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2, hpa-cpu hpa-varga, }
AUTOSCALER_CONFIGURATION=$2 #{DHALION=scale-down-factor, DS2=OVERPROVISIONING_FACTOR, HPA_CPU=TARGET_VALUE, HPA_VARGA=UTILIZATION_TARGET_VALUE}
QUERY=$3
MODE=$4 #{reactive, non-reactive}
AVAILABLE_TASKMANAGERS=$5
NAMESPACE=$6

if [ "$AUTOSCALER" == "dhalion" ] || [ "$AUTOSCALER" == "ds2" ] || [ "$AUTOSCALER" == "hpa-cpu" ] || [ "$AUTOSCALER" == "hpa-varga" ]
then
  echo "Deploying autoscaler $AUTOSCALER with configuration $AUTOSCALER_CONFIGURATION on query $QUERY with mode $MODE setting available_taskmanagers=$AVAILABLE_TASKMANAGERS in namespace $NAMESPACE"
else
  echo "Autoscaler $AUTOSCALER was not recognized. Canceling autoscaler deployment"
  exit 1
fi

export AVAILABLE_TASKMANAGERS=$AVAILABLE_TASKMANAGERS
export NAMESPACE=$NAMESPACE
export CONFIGURATION=$AUTOSCALER_CONFIGURATION
if [ "$MODE" == "reactive" ]
then
  kubectl apply -f ../yamls/autoscalers/autoscaler_reactive_rbac_rules.yaml
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_reactive.yaml | kubectl apply -f -
else
  envsubst < ../yamls/autoscalers/autoscaler_non_reactive_rbac_rules.yaml | kubectl apply -f -
  export QUERY=$QUERY
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_non-reactive.yaml | kubectl apply -f -
fi



