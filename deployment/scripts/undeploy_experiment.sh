#!/bin/bash

query=$1
autoscaler=$2

echo "Undeploying experiment Query=$query autoscaler=$autoscaler"
source ./scripts/undeploy_autoscaler.sh $autoscaler
source ./scripts/undeploy_queries.sh $query
sleep 60s
source ./scripts/undeploy_nfs.sh
echo "Finished undeploying experiment"