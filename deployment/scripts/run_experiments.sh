#!/bin/bash

input="experiments/experiments.txt"
while IFS= read -r line
do
  printf 'Run experiment: %s\n' "$line"
  IFS=';' read -ra ss <<< "$line"
  query="${ss[0]}"
  autoscaler="${ss[1]}"
  metric="${ss[2]}"
  echo "Query: $query\nAutoscaler: $autoscaler\Metric: $metric\n"
done

echo "Deploying"
#source ./scripts/deploy_nfs.sh
#source ./scripts/deploy_queries.sh
#source ./scripts/deploy_autoscaler.sh dhalion 05

echo "Running experiments"

echo "Fetchin results from prometheus server"


echo "Undeploying"
#source ./scripts/undeploy_autoscaler.sh
#source ./scripts/undeploy_queries.sh
#source ./scripts/undeploy_nfs.sh

echo "Finished undeploying"
