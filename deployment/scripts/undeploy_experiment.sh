#!/bin/bash

QUERY=$1                      #{1, 2, 3, 5, 8, 11}
MODE=$2                       #{reactive, non-reactive}
AUTOSCALER=$3

echo "Undeploying experiment Query=$QUERY MODE=$MODE AUTOSCALER=$AUTOSCALER"
source ./undeploy_autoscaler.sh $AUTOSCALER $MODE
source ./undeploy_queries.sh $QUERY $MODE
# Ensure all pods using nfs are shut down before undeploying nfs
#sleep 60s
source ./undeploy_nfs.sh
echo "Finished undeploying experiment"