#!/bin/bash

run_local=true

# Experiment configurations to run the experiments in
file0=../experiments/query_1_experiments.txt

# input
line=""
# generates
query=""
autoscaler=""
metric=""
function parseLine() {
  # default values
  query=""
  autoscaler=""
  metric=""
  i=0
  for w in $(echo "$line" | tr ";" "\n"); do
    if [ "$i" -eq 0 ]
    then
      query="$w"
    elif [ "$i" -eq 1 ]
    then
      autoscaler="$w"
    elif [ "$i" -eq 2 ]
    then
      metric="$w"
    elif [ "$i" -eq 3]
    then
      mode="$w"
    fi
    i=$((i+1))
  done
}

function deployExperiment() {
    parseLine
    echo "Deploying experiment with namespace=$namespace query=$query autoscaler=$autoscaler metric=$metric mode=$mode"
    source ./deploy_experiment.sh "$query" "$autoscaler" "$metric" "$mode"
}

function fetchExperiments() {
    parseLine
    echo "Fetching data from namespace=$namespace query=$query autoscaler=$autoscaler metric=$metric"
    source ./fetch_prometheus_results.sh "$query" "$autoscaler" "$metric" "$run_local"
}

function undeployExperiments() {
  parseLine
  echo "Undeploying experiment with namespace=$namespace query=$query autoscaler=$autoscaler mode=$mode"
  source ./undeploy_experiment.sh "$query" "$autoscaler" "$mode"
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
