#!/bin/bash

EXPERIMENT_TAG=$1

# Fetch snapshot of prometheus deploy
PROMETHEUS_POD="$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)"
echo "Port forwarding prometheus server ($PROMETHEUS_POD)"
kubectl port-forward "$PROMETHEUS_POD" 9090 &

sleep 5s
echo "Fetching prometheus snapshot..."
RESPONSE=$(curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot)
SNAPSHOT_STATUS=$(echo "$RESPONSE" | sed 's/{//g' | sed 's/}//g' | cut -d "," -f1 | cut -d ":" -f2 | sed 's/"//g' )
if [ "$SNAPSHOT_STATUS" = "success" ]
then
  SNAPSHOT_FILE=$(echo "$RESPONSE" | sed 's/{//g' | sed 's/}//g' | cut -d "," -f2 | cut -d ":" -f3 | sed 's/"//g')
  echo "Creating a snapshot was successful (name = $SNAPSHOT_FILE)"
  kubectl cp "$(kubectl get pods| grep prometheus-server- | awk '{print $1}')":/prometheus/snapshots/"$SNAPSHOT_FILE" -c prometheus-server ../../../results/snapshots/"$EXPERIMENT_TAG"
else
  echo "Creating a snapshot failed: $RESPONSE"
fi

echo "Removing port forward of prometheus server ($PROMETHEUS_POD)"
ps -aux | grep "kubectl port-forward $PROMETHEUS_POD" | grep -v grep | awk {'print $2'} | xargs kill



## Fetch data from prometheus deploy
#if [ "$run_local" = true ]
#  then
#      echo "Fetching data from local prometheus pod with query=$query autoscaler=$autoscaler metric=$metric run_local=$run_local"
#      PROMETHEUS_POD=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)
#      echo "Found Prometheus pod: $PROMETHEUS_POD"
#      kubectl port-forward "$PROMETHEUS_POD" 9090 &
#      sleep 60s
#      python3 ../data_processing localhost "query-$query" $autoscaler $metric "cosine-60"
#      sleep 5s
#      echo "Deleting port-forward"
#      ps -aux | grep "kubectl port-forward $PROMETHEUS_POD" | grep -v grep | awk {'print $2'} | xargs kill
#  else
#      echo "Fetching data from external prometheus pod with query=$query autoscaler=$autoscaler metric=$metric run_local=$run_local"
#      prometheus_IP=$(kubectl get svc my-external-prometheus -o yaml | grep ip: | awk '{print $3}')
#      python3 ../data_processing $prometheus_IP "query-$query" $autoscaler $metric "cosine-60"
#fi

sleep 30s
echo "Fetched data from prometheus server"