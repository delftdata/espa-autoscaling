#!/bin/bash

query=$1
autoscaler=$2
metric=$3
run_local=$4

if [ "$run_local" = true ]
  then
      echo "Fetching data from local prometheus pod with query=$query autoscaler=$autoscaler metric=$metric run_local=$run_local"
      PROMETHEUS_POD=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)
      echo "Found Prometheus pod: $PROMETHEUS_POD"
      kubectl port-forward "$PROMETHEUS_POD" 9090 &
      sleep 60s
      python3 ../data_processing localhost "query-$query" $autoscaler $metric "cosine-60"
      sleep 5s
      echo "Deleting port-forward"
      ps -aux | grep "kubectl port-forward $PROMETHEUS_POD" | grep -v grep | awk {'print $2'} | xargs kill
  else
      echo "Fetching data from external prometheus pod with query=$query autoscaler=$autoscaler metric=$metric run_local=$run_local"
      prometheus_IP=$(kubectl get svc my-external-prometheus -o yaml | grep ip: | awk '{print $3}')
      python3 ../data_processing $prometheus_IP "query-$query" $autoscaler $metric "cosine-60"
fi

sleep 30s
echo "Fetched data from prometheus server"