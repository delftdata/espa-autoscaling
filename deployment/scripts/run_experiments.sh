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
  source ./scripts/deploy_queries.sh $query
  source ./scripts/deploy_autoscaler.sh $autoscaler $metric

  echo "Finished deployment"

  sleep 140m

  prometheus_IP=$(kubectl get svc my-external-prometheus -o yaml | grep ip: | awk '{print $3}')
  python3 ./data_processing $prometheus_IP "query-$query" $autoscaler $metric "cosine-60"

  sleep 30s

  echo "Processed data. Starting undeploying cluster..."
  source ./scripts/undeploy_autoscaler.sh $autoscaler
  source ./scripts/undeploy_queries.sh $query
  source ./scripts/undeploy_nfs.sh
  echo "Finished undeployment"

  sleep 1m
done < "$input"

echo "Finished experiments"

