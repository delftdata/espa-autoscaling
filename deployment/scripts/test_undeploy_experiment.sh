#!/bin/bash

query=$1
autoscaler=$2
mode=$3

echo "Deploying experiment with: Query=$query autoscaler=$autoscaler metric=$metric"
source ./test_undeploy_autoscalers.sh $autoscaler $query $mode
source ./test_undeploy_queries.sh $query $mode
source ./undeploy_nfs.sh
echo "Finished deployment"