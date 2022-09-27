#!/bin/bash


input="./experiments/experiments.txt"
run_local=false

if [ $# -ge 1 ]
  then
    input=$1
fi
if [ $# -ge 2 ]
  then
    run_local=$2
fi

if [ "$run_local" = true ]
then
  echo "Starting experiments from $input with a local prometheus server"
else
  echo "Starting experiments from $input with an externally exposed prometheus server"
fi

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

if [ "$run_local" = true ]
then
    echo "Fetching data from local prometheus pod"
    JOB_MANAGER_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)
    kubectl port-forward $JOB_MANAGER_NAME 9090 &
    sleep 20s
    python3 ./data_processing "localhost" "query-$query" $autoscaler $metric "cosine-60"
  else
    echo "Fetching data from external prometheus pod"
    prometheus_IP=$(kubectl get svc my-external-prometheus -o yaml | grep ip: | awk '{print $3}')
    python3 ./data_processing $prometheus_IP "query-$query" $autoscaler $metric "cosine-60"
fi

  sleep 30s

  echo "Processed data. Starting undeploying cluster..."
  source ./scripts/undeploy_autoscaler.sh $autoscaler
  source ./scripts/undeploy_queries.sh $query
  source ./scripts/undeploy_nfs.sh
  echo "Finished undeployment"

  sleep 1m
done < "$input"

echo "Finished experiments"

