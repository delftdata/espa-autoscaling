#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2, hpa-cpu hpa-varga, }
QUERY=$2
MODE=$3 #{reactive, non-reactive}
AVAILABLE_TASKMANAGERS=$4
NAMESPACE=$5

if [ "$AUTOSCALER" == "dhalion" ] || [ "$AUTOSCALER" == "ds2" ] || [ "$AUTOSCALER" == "hpa-cpu" ]
then
  echo "Deploying autoscaler $AUTOSCALER on query $QUERY with mode $MODE setting available_taskmanagers=$AVAILABLE_TASKMANAGERS in namespace $NAMESPACE"
else
  echo "Autoscaler $AUTOSCALER was not recognized. Canceling autoscaler deployment"
  exit 1
fi

export AVAILABLE_TASKMANAGERS=$AVAILABLE_TASKMANAGERS
export NAMESPACE=$NAMESPACE
if [ "$MODE" == "reactive" ]
then
  kubectl apply -f ../yamls/autoscalers/autoscaler_reactive_rbac_rules.yaml
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_reactive.yaml | kubectl apply -f -
else
  kubectl apply -f ../yamls/autoscalers/autoscaler_non_reactive_rbac_rules.yaml
  export QUERY=$QUERY
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_non-reactive.yaml | kubectl apply -f -
fi



