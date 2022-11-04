#!/bin/bash

query=$1
autoscaler=$2
mode=$3

echo "Undeploying experiment Query=$query autoscaler=$autoscaler"
source ./scripts/undeploy_autoscaler.sh $autoscaler $mode
source ./scripts/undeploy_queries.sh $query $mode
sleep 60s
source ./scripts/undeploy_nfs.sh
echo "Finished undeploying experiment"