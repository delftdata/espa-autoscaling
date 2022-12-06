#!/bin/bash

QUERY=$1                      #{1, 2, 3, 5, 8, 11}
MODE=$2                       #{reactive, non-reactive}
AUTOSCALER=$3
INPUT_RATE_MEAN=$4            # Mean of Cosinus pattern
INPUT_RATE_MAX_DIVERGENCE=$5

echo "Deploying experiment with: Query=$QUERY MODE=$MODE AUTOSCALER=$AUTOSCALER INPUT_RATE_MEAN=$INPUT_RATE_MEAN INPUT_RATE_MAX_DIVERGENCE=$INPUT_RATE_MAX_DIVERGENCE"
source ./deploy_nfs.sh
source ./deploy_queries.sh $QUERY $MODE $INPUT_RATE_MEAN $INPUT_RATE_MAX_DIVERGENCE
source ./deploy_autoscaler.sh $MODE $AUTOSCALER
echo "Finished deployment"