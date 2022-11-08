#!/bin/bash

query=$1
autoscaler=$2
metric=$3
mode=$4

echo "Deploying experiment with: Query=$query autoscaler=$autoscaler metric=$metric"
source ./deploy_nfs.sh
source ./deploy_queries.sh $query $mode
source ./deploy_autoscaler.sh $autoscaler $metric $query $mode
echo "Finished deployment"