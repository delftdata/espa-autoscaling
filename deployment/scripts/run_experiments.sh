#!/bin/bash

input="experiments/experiments.txt"
echo "Starting experiments from $input"

while IFS= read -r line
do
  IFS=';' read -ra ss <<< "$line"
  query="${ss[0]}"
  autoscaler="${ss[1]}"
  metric="${ss[2]}"

  echo "Deploying experiment with: Query=$query autoscaler=$autoscaler metric=$metric"
  source ./scripts/deploy_nfs.sh
  source ./scripts/deploy_queries.sh query
  source ./scripts/deploy_autoscaler.sh $dhalion $metric

  wait 180

  echo "Undeploying..."
  source ./scripts/undeploy_autoscaler.sh $autoscaler
  source ./scripts/undeploy_queries.sh $query
  source ./scripts/undeploy_nfs.sh
done < "$input"

echo "Finished experiments"

