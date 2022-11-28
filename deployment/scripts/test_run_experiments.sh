#!/bin/bash

run_local=true

# Experiment configurations to run the experiments in
file0=../experiments/test_experiments.txt

# input
namespace=""
line=""
# generates
query=""
autoscaler=""
mode=""
input_rate_mean=""
input_rate_max_divergence=""
function parseLine() {
# default values
query=""
autoscaler=""
mode=""
input_rate_mean=""
input_rate_max_divergence=""
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
      mode="$w"
    elif [ "$i" -eq 3 ]
    then
      input_rate_mean="$w"
    elif [ "$i" -eq 4 ]
    then
      input_rate_max_divergence="$w"
    fi
    i=$((i+1))
  done
}

function deployExperiment() {
    parseLine
    echo "Deploying experiment with  query=$query autoscaler=$autoscaler mode=$mode input_Rate-mean=$input_rate_mean input_rate_max_divergence=$input_rate_max_divergence"
    source ./test_deploy_experiment.sh "$query" "$autoscaler" "$mode" "$input_rate_mean" "$input_rate_max_divergence"
}

function fetchExperiments() {
    parseLine
    echo "Fetching data from namespace=$namespace query=$query autoscaler=$autoscaler metric=$mode-$input_rate_mean-$input_rate_max_divergence"
    source ./fetch_prometheus_results.sh "$query" "$autoscaler" "$mode-$input_rate_mean-$input_rate_max_divergence" "$run_local"
}

function undeployExperiments() {
  parseLine
  echo "Undeploying experiment with namespace=$namespace query=$query autoscaler=$autoscaler mode=$mode"

  minikube profile "$namespace"
  source ./test_undeploy_experiment.sh "$query" "$autoscaler" "$mode"
}

paste -d@ $file0  | while IFS="@" read -r e0
do
  echo "Starting deploying all containers"
  line="$e0"
  deployExperiment

  echo "Finished deploying all containers"

  sleep 60m

  echo "Starting to collect all data"
  line="$e0"
  fetchExperiments

  echo "Finished collecting all data"

  sleep 30s

  echo "Starting undeploying all containers"
  line="$e0"
  undeployExperiments

  echo "Finished undeploying all containers"

  sleep 1m
done
