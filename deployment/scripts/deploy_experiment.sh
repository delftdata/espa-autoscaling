#!/bin/bash

QUERY=$1                      #{1, 2, 3, 5, 8, 11}
MODE=$2                       #{reactive, non-reactive}
INITIAL_PARALLELISM=$3
AUTOSCALER=$4
INPUT_RATE_MEAN=$5           # Mean of Cosinus pattern
INPUT_RATE_MAX_DIVERGENCE=$6

echo "Deploying experiment with: Query=$QUERY MODE=$MODE INITIAL_PARALLELISM=$INITIAL_PARALLELISM AUTOSCALER=$AUTOSCALER INPUT_RATE_MEAN=$INPUT_RATE_MEAN INPUT_RATE_MAX_DIVERGENCE=$INPUT_RATE_MAX_DIVERGENCE"
source ./deploy_nfs.sh
source ./deploy_queries.sh $QUERY $MODE $INITIAL_PARALLELISM $INPUT_RATE_MEAN $INPUT_RATE_MAX_DIVERGENCE
source ./deploy_autoscaler.sh $MODE $AUTOSCALER
echo "Finished deployment"