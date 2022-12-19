#!/bin/bash

# Experiment configurations to run the experiments in
file0=../experiments/experiments.txt

# input
line=""
# generates
QUERY=""
MODE=""
INITIAL_PARALLELISM=""
AVAILABLE_TASKMANAGERS=""
AUTOSCALER=""
INPUT_RATE_MEAN=""
INPUT_RATE_MAX_DIVERGENCE=""
NAMESPACE=""
EXPERIMENT_LABEL=""

# Additional identifier of an experiment that adds [{EXPIMENT_TAG}] to the identifier. This can be used to distinguish
# similar experimental runs from each other.
EXPERIMENT_TAG=""

function parseLine() {
  # default values
  QUERY=""
  MODE=""
  INITIAL_PARALLELISM=""
  AVAILABLE_TASKMANAGERS=""
  AUTOSCALER=""
  INPUT_RATE_MEAN=""
  INPUT_RATE_MAX_DIVERGENCE=""
  NAMESPACE=""
  EXPERIMENT_LABEL=""
  i=0
  for w in $(echo "$line" | tr ";" "\n"); do
    if [ "$i" -eq 0 ]
    then
      QUERY="$w"
    elif [ "$i" -eq 1 ]
    then
      MODE="$w"
    elif [ "$i" -eq 2 ]
    then
      INITIAL_PARALLELISM="$w"
    elif [ "$i" -eq 3 ]
    then
      AVAILABLE_TASKMANAGERS="$w"
    elif [ "$i" -eq 4 ]
    then
      AUTOSCALER="$w"
    elif [ "$i" -eq 5 ]
    then
      INPUT_RATE_MEAN="$w"
    elif [ "$i" -eq 6 ]
    then
      INPUT_RATE_MAX_DIVERGENCE="$w"
    elif [ "$i" -eq 7 ]
    then
      NAMESPACE="$w"
    elif [ "$i" -eq 8 ]
    then
      EXPERIMENT_LABEL="$w"
    fi
    i=$((i+1))
  done
}

function deployExperiment() {
    parseLine
    echo "Deploying experiment with QUERY=$QUERY MODE=$MODE INITIAL_PARALLELISM=$INITIAL_PARALLELISM AVAILABLE_TASKMANAGERS=$AVAILABLE_TASKMANAGERS AUTOSCALER=$AUTOSCALER INPUT_RATE_MEAN=$INPUT_RATE_MEAN INPUT_RATE_MAX_DIVERGENCE=$INPUT_RATE_MAX_DIVERGENCE"
    source ./deploy_experiment.sh "$QUERY" "$MODE" "$INITIAL_PARALLELISM" "$AVAILABLE_TASKMANAGERS" "$AUTOSCALER" "$INPUT_RATE_MEAN" "$INPUT_RATE_MAX_DIVERGENCE" "$NAMESPACE"
}

function fetchExperiments() {
    parseLine
    echo "Fetching data from QUERY=$QUERY AUTOSCALER=$AUTOSCALER EXPERIMENT_LABEL=$EXPERIMENT_LABEL"
    source ./fetch_experiment_results.sh "$QUERY" "$MODE" "$AUTOSCALER" "$EXPERIMENT_LABEL" "$EXPERIMENT_TAG"
}

function undeployExperiments() {
  parseLine
  echo "Undeploying experiment with QUERY=$QUERY AUTOSCALER=$AUTOSCALER MODE=$MODE"
  source ./undeploy_experiment.sh "$QUERY" "$MODE" "$AUTOSCALER" "$NAMESPACE"
}

paste -d@ $file0 | while IFS="@" read -r e0
do
  line="$e0"

  echo "Deploying all containers"
  deployExperiment
  echo "Finished deploying all containers"

  sleep 140m

  echo "Collect all data"
  fetchExperiments
  echo "Finished collecting all data."

  sleep 30s

  echo "Undeploying all containers"
  undeployExperiments
  echo "Finished undeploying all containers"

  sleep 1m
done
