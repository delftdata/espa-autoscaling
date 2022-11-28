#!/bin/bash

query=$1
autoscaler=$2
mode=$3
INPUT_RATE_MEAN=$4
INPUT_RATE_MAX_DIVERGENCE=$5

echo "Deploying experiment with: Query=$query autoscaler=$autoscaler INPUT_RATE_MEAN=$INPUT_RATE_MEAN INPUT_RATE_MAX_DIVERGENCE=$INPUT_RATE_MAX_DIVERGENCE"
source ./deploy_nfs.sh
source ./test_deploy_queries.sh "$query" "$mode" "$INPUT_RATE_MEAN" "$INPUT_RATE_MAX_DIVERGENCE"
source ./test_deploy_autoscalers.sh "$autoscaler" "$query" "$mode"
echo "Finished deployment"