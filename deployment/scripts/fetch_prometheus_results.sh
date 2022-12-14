#!/bin/bash

QUERY=$1
AUTOSCALER=$2
EXPERIMENT_TAG=$3

PROMETHEUS_POD="$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)"
echo "Port forwarding prometheus server ($PROMETHEUS_POD)"
kubectl port-forward "$PROMETHEUS_POD" 9090 &
sleep 5s

# Save autoscaler logs
AUTOSCALER_POD=$(kubectl get pods | grep "$AUTOSCALER" | awk '{print $1}')
AUTOSCALER_LOG_DIRECTORY="../../../results/logs/$EXPERIMENT_TAG/"
mkdir -p "$AUTOSCALER_LOG_DIRECTORY"
kubectl logs "$(kubectl get pods | grep hpa-cpu | awk '{print $1}')" > "$AUTOSCALER_LOG_DIRECTORY/$AUTOSCALER_POD.log"
echo "Fetched logs from $AUTOSCALER_POD"

# Fetch snapshot of prometheus deploy
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

# Fetching data from prometheus
python3 ../data_processing_old localhost "query-$QUERY" "$AUTOSCALER" "$EXPERIMENT_TAG" "cosine-60"


echo "Removing port forward of prometheus server ($PROMETHEUS_POD)"
ps -aux | grep "kubectl port-forward $PROMETHEUS_POD" | grep -v grep | awk {'print $2'} | xargs kill
