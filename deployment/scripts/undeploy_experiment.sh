#!/bin/bash

QUERY=$1                      #{1, 2, 3, 5, 8, 11}
MODE=$2                       #{reactive, non-reactive}
AUTOSCALER=$3
NAMESPACE=$4

echo "Undeploying experiment Query=$QUERY MODE=$MODE AUTOSCALER=$AUTOSCALER"
source ./undeploy_autoscaler.sh $AUTOSCALER $MODE
source ./undeploy_queries.sh $QUERY $MODE
source ./undeploy_nfs.sh $NAMESPACE
echo "Finished undeploying experiment"