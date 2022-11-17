#!/bin/bash

run_local=true

# Minikube profiles to run the experiments in
ns0="autoscaling-q1"
ns1="autoscaling-q2"
ns2="autoscaling-q3"

# Experiment configurations to run the experiments in
file0=../experiments/query_1_experiments.txt
file1=../experiments/query_3_experiments.txt
file2=../experiments/query_11_experiments.txt

# input
namespace=""
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
    minikube profile "$namespace"
    source ./deploy_experiment.sh "$query" "$autoscaler" "$metric" "$mode"
}

function fetchExperiments() {
    parseLine
    echo "Fetching data from namespace=$namespace query=$query autoscaler=$autoscaler metric=$metric"

    minikube profile "$namespace"
    source ./fetch_prometheus_results.sh "$query" "$autoscaler" "$metric" "$run_local"
}

function undeployExperiments() {
  parseLine
  echo "Undeploying experiment with namespace=$namespace query=$query autoscaler=$autoscaler mode=$mode"

  minikube profile "$namespace"
  source ./undeploy_experiment.sh "$query" "$autoscaler" "$mode"
}

paste -d@ $file0 $file1 $file2  | while IFS="@" read -r e0 e1 e2
do
  echo "Starting deploying all containers"
  namespace="$ns0"
  line="$e0"
  deployExperiment

  namespace="$ns1"
  line="$e1"
  deployExperiment

  namespace="$ns2"
  line="$e2"
  deployExperiment

  echo "Finished deploying all containers"

  sleep 140m

  echo "Starting to collect all data"
  namespace="$ns0"
  line="$e0"
  fetchExperiments

  namespace="$ns1"
  line="$e1"
  fetchExperiments

  namespace="$ns2"
  line="$e2"
  fetchExperiments
  echo "Finished collecting all data"

  sleep 30s

  echo "Starting undeploying all containers"
  namespace="$ns0"
  line="$e0"
  undeployExperiments

  namespace="$ns1"
  line="$e1"
  undeployExperiments

  namespace="$ns2"
  line="$e2"
  undeployExperiments
  echo "Finished undeploying all containers"

  sleep 1m
done
