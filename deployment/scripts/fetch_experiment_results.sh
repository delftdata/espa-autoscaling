#!/bin/bash

PROMETHEUS_IP="localhost"
PROMETHEUS_PORT="9090"
EXPERIMENT_LENGTH_MINUTES=150 # we want to make sure we fetch all data of the experiment
DATA_STEP_SIZE_SECONDS=15

QUERY=$1
MODE=$2
LOAD_PATTERN=$3
AUTOSCALER=$4
AUTOSCALER_CONFIGURATION=$5

# Overall identifier shared by multiple experiments. Experiment_label is used as the name of the folder in which the
# experiment's results are stored
EXPERIMENT_LABEL=$6

# Tag is an additional non-required identifier of the current experiment run. This can be used to distinguish 2
# similar experiments with the same experiment_label from each other. EXPERIMENT_TAG={", "none", "undef", "undefined"}
# will disable the tag
EXPERIMENT_TAG=$7

# If experiment_tag
if [ "$EXPERIMENT_TAG" = "" ] || [ "$EXPERIMENT_TAG" = "none" ] || [ "$EXPERIMENT_TAG" = "undef" ] || [ "$EXPERIMENT_TAG" = "undefined" ]
then
  EXPERIMENT_TAG=""
else
  EXPERIMENT_TAG="[$EXPERIMENT_TAG]"
fi

# Only add mode to experiment_identifier when not default value (non-reactive)
if [ "$MODE" = "non-reactive" ]
then
  MODE=""
else
  MODE="_$MODE"
fi

# Only add load_pattern to experiment_identifier when not default value (cosinus)
if [ "$LOAD_PATTERN" = "cosinus" ]
then
  LOAD_PATTERN=""
else
  LOAD_PATTERN="($LOAD_PATTERN)"
fi

EXPERIMENT_IDENTIFIER="${EXPERIMENT_TAG}q${QUERY}${LOAD_PATTERN}_${AUTOSCALER}($AUTOSCALER_CONFIGURATION)${MODE}"
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
kubectl logs "$AUTOSCALER_POD" > "$AUTOSCALER_LOG_FILE"
echo "Successfully saved logs of $AUTOSCALER_POD at $AUTOSCALER_LOG_FILE"

JOBMANAGER_POD=$(kubectl get pods | grep "flink-jobmanager-" | awk '{print $1}')
JOBMANAGER_LOG_FILE="$LOG_DIRECTORY/$JOBMANAGER_POD.log"
kubectl logs "$JOBMANAGER_POD" > "$JOBMANAGER_LOG_FILE"
echo "Successfully saved logs of final jobmanager $JOBMANAGER_POD at $JOBMANAGER_LOG_FILE"

WORKBENCH_POD=$(kubectl get pods | grep "workbench" | awk '{print $1}')
WORKBENCH_LOG_FILE="$LOG_DIRECTORY/$WORKBENCH_POD.log"
kubectl logs "$WORKBENCH_POD" > "$WORKBENCH_LOG_FILE"
echo "Successfully saved logs of workbench $WORKBENCH_POD at $WORKBENCH_LOG_FILE"

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
python3 ../data_fetching "$PROMETHEUS_IP" "$PROMETHEUS_PORT" "$EXPERIMENT_LENGTH_MINUTES" "$DATA_STEP_SIZE_SECONDS" "$DATA_DIRECTORY" "$EXPERIMENT_IDENTIFIER"


# Remove port forward
echo "Removing port forward of prometheus server ($PROMETHEUS_POD)"
ps -aux | grep "kubectl port-forward $PROMETHEUS_POD" | grep -v grep | awk {'print $2'} | xargs kill
