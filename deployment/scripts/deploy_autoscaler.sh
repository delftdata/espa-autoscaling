#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2, hpa-cpu hpa-varga, }
QUERY=$2
MODE=$3 #{reactive, non-reactive}
AVAILABLE_TASKMANAGERS=$4

if [ "$AUTOSCALER" == "dhalion" ] || [ "$AUTOSCALER" == "ds2" ] || [ "$AUTOSCALER" == "hpa-cpu" ]
then
  echo "Deploying autoscaler $AUTOSCALER on query $QUERY with mode $MODE setting AVAILABLE_TASKMANAGERS=$AVAILABLE_TASKMANAGERS"
else
  echo "Autoscaler $AUTOSCALER was not recognized. Canceling autoscaler deployment"
  exit 1
fi

kubectl apply -f ../yamls/autoscalers/autoscaler_rbac_rules.yaml
export AVAILABLE_TASKMANAGERS=$AVAILABLE_TASKMANAGERS
if [ "$MODE" == "reactive" ]
then
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_reactive.yaml | kubectl apply -f -
else
  export QUERY=$QUERY
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_non-reactive.yaml | kubectl apply -f -
fi



