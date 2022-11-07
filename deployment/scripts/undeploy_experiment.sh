#!/bin/bash

query=$1
autoscaler=$2
mode=$3

echo "Undeploying experiment Query=$query autoscaler=$autoscaler"
source ./undeploy_autoscaler.sh $autoscaler $mode
source ./undeploy_queries.sh $query $mode
sleep 60s
source ./undeploy_nfs.sh
echo "Finished undeploying experiment"