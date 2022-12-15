#!/bin/bash

PROMETHEUS_IP="localhost"
PROMETHEUS_PORT="9090"
EXPERIMENT_LENGTH_MINUTES=140
DATA_STEP_SIZE_SECONDS=15

QUERY=$1
MODE=$2
AUTOSCALER=$3
EXPERIMENT_LABEL=$4
EXPERIMENT_TAG=$5

if [ "$EXPERIMENT_TAG" = "" ] || [ "$EXPERIMENT_TAG" = "none" ] || [ "$EXPERIMENT_TAG" = "undef" ] || [ "$EXPERIMENT_TAG" = "undefined" ]
then
  EXPERIMENT_TAG=""
else
  EXPERIMENT_TAG="[$EXPERIMENT_TAG]"
fi

if [ "$MODE" = "non-reactive" ]
then
  MODE=""
else
  MODE="_$MODE"
fi

EXPERIMENT_IDENTIFIER="${EXPERIMENT_TAG}q${QUERY}_${AUTOSCALER}${MODE}"
echo "Fetching data for $EXPERIMENT_IDENTIFIER"

SAVE_DIRECTORY="$HOME/results/$EXPERIMENT_LABEL"

LOG_DIRECTORY="$SAVE_DIRECTORY/logs/$EXPERIMENT_IDENTIFIER"
SNAPSHOT_DIRECTORY="$SAVE_DIRECTORY/snapshots/$EXPERIMENT_IDENTIFIER"
DATA_DIRECTORY="$SAVE_DIRECTORY/data"
mkdir -p "$LOG_DIRECTORY" "$SNAPSHOT_DIRECTORY" "$DATA_DIRECTORY"

PROMETHEUS_POD="$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)"
echo "Port forwarding prometheus server ($PROMETHEUS_POD)"
kubectl port-forward "$PROMETHEUS_POD" 9090 &
sleep 5s

# Save autoscaler logs
AUTOSCALER_POD=$(kubectl get pods | grep "$AUTOSCALER" | awk '{print $1}')
AUTOSCALER_LOG_FILE="$LOG_DIRECTORY/$AUTOSCALER_POD.log"
kubectl logs "$(kubectl get pods | grep hpa-cpu | awk '{print $1}')" > AUTOSCALER_LOG_FILE
echo "Successfully saved logs of $AUTOSCALER_POD at $AUTOSCALER_LOG_FILE"

# Fetch snapshot of prometheus deploy
echo "Fetching prometheus snapshot..."
RESPONSE=$(curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot)
SNAPSHOT_STATUS=$(echo "$RESPONSE" | sed 's/{//g' | sed 's/}//g' | cut -d "," -f1 | cut -d ":" -f2 | sed 's/"//g' )
if [ "$SNAPSHOT_STATUS" = "success" ]
then
  SNAPSHOT_FILE=$(echo "$RESPONSE" | sed 's/{//g' | sed 's/}//g' | cut -d "," -f2 | cut -d ":" -f3 | sed 's/"//g')
  kubectl cp "$(kubectl get pods| grep prometheus-server- | awk '{print $1}')":/prometheus/snapshots/"$SNAPSHOT_FILE" -c prometheus-server "$SNAPSHOT_DIRECTORY"
  echo "Successfully saved prometheus snapshot $SNAPSHOT_FILE at $SNAPSHOT_DIRECTORY/"
else
  echo "Creating a snapshot failed: $RESPONSE"
fi


# Fetching data from prometheus
python3 ../data_processing "$PROMETHEUS_IP" "$PROMETHEUS_PORT" "$EXPERIMENT_LENGTH_MINUTES" "$DATA_STEP_SIZE_SECONDS" "$DATA_DIRECTORY" "$EXPERIMENT_IDENTIFIER"


# Remove port forward
echo "Removing port forward of prometheus server ($PROMETHEUS_POD)"
ps -aux | grep "kubectl port-forward $PROMETHEUS_POD" | grep -v grep | awk {'print $2'} | xargs kill
