#!/bin/bash

AUTOSCALER=$1 #{dhalion, ds2, hpa-cpu hpa-varga, }
MODE=$2 #{reactive, non-reactive}

if [ "$AUTOSCALER" == "dhalion" ] || [ "$AUTOSCALER" == "ds2" ] || [ "$AUTOSCALER" == "hpa-cpu" ]
then
  echo "Undeploying autoscaler $AUTOSCALER with mode $MODE."
else
  echo "Autoscaler $AUTOSCALER was not recognized. Canceling autoscaler undeployment."
  exit 1
fi

if [ "$MODE" == "reactive" ]
then
  kubectl delete -f ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_reactive.yaml
else
  kubectl delete -f ../yamls/autoscalers/"${AUTOSCALER}"/deployment_"${AUTOSCALER}"_non-reactive.yaml
fi
kubectl delete -f ../yamls/autoscalers/autoscaler_rbac_rules.yaml

