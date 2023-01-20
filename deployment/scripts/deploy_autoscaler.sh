#!/bin/bash

QUERY=${1}
MODE=${2} #{reactive, non-reactive}
AVAILABLE_TASKMANAGERS=${3}
NAMESPACE=${4}
AUTOSCALER=${5}
AUTOSCALER_CONFIGURATION_0=${6}
AUTOSCALER_CONFIGURATION_1=${7}
AUTOSCALER_CONFIGURATION_2=${8}


if [ "$AUTOSCALER" == "dhalion" ] || [ "$AUTOSCALER" == "ds2" ] || [ "$AUTOSCALER" == "hpa-cpu" ] || [ "$AUTOSCALER" == "hpa-varga" ]
then
  echo "Deploying autoscaler ${AUTOSCALER}[${AUTOSCALER_CONFIGURATION_0},${AUTOSCALER_CONFIGURATION_1},${AUTOSCALER_CONFIGURATION_2}]
        on query ${QUERY} with mode ${MODE} setting available_taskmanagers=${AVAILABLE_TASKMANAGERS} in namespace ${NAMESPACE}.
        "
else
  echo "Autoscaler ${AUTOSCALER} was not recognized. Canceling autoscaler deployment"
  exit 1
fi

export AVAILABLE_TASKMANAGERS=${AVAILABLE_TASKMANAGERS}
export NAMESPACE=${NAMESPACE}
export AUTOSCALER_CONFIGURATION_0=${AUTOSCALER_CONFIGURATION_0}
export AUTOSCALER_CONFIGURATION_1=${AUTOSCALER_CONFIGURATION_1}
export AUTOSCALER_CONFIGURATION_2=${AUTOSCALER_CONFIGURATION_2}
if [ "$MODE" == "reactive" ]
then
  kubectl apply -f ../yamls/autoscalers/autoscaler_reactive_rbac_rules.yaml
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_reactive.yaml | kubectl apply -f -
else
  envsubst < ../yamls/autoscalers/autoscaler_non_reactive_rbac_rules.yaml | kubectl apply -f -
  export QUERY=${QUERY}
  envsubst < ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_non-reactive.yaml | kubectl apply -f -
fi



