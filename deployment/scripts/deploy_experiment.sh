#!/bin/bash

query=$1
autoscaler=$2
metric=$3

echo "Deploying experiment with: Query=$query autoscaler=$autoscaler metric=$metric"
source ./scripts/deploy_nfs.sh
source ./scripts/deploy_queries.sh $query
source ./scripts/deploy_autoscaler.sh $autoscaler $metric $query
echo "Finished deployment"