#!/bin/bash

# Experiment configurations to run the experiments in
EXPERIMENT_FILE=../experiments/experiments.txt

# input
line=""
# generates
QUERY=""
MODE=""
INITIAL_PARALLELISM=""
AVAILABLE_TASKMANAGERS=""
AUTOSCALER=""
AUTOSCALER_CONFIGURATION_0=""
AUTOSCALER_CONFIGURATION_1=""
AUTOSCALER_CONFIGURATION_2=""
LOAD_PATTERN=""
EXPERIMENT_DURATION=""
WORKLOAD_CONFIGURATION_0=""
WORKLOAD_CONFIGURATION_1=""
WORKLOAD_CONFIGURATION_2=""
WORKLOAD_CONFIGURATION_3=""
NAMESPACE=""
EXPERIMENT_LABEL=""
# Additional identifier of an experiment that adds [{EXPIMENT_TAG}] to the identifier. This can be used to distinguish
# similar experimental runs from each other.
EXPERIMENT_TAG=""

function parseLine() {
  # default values
  QUERY=""
  MODE=""
  INITIAL_PARALLELISM=""
  AVAILABLE_TASKMANAGERS=""
  AUTOSCALER=""
  AUTOSCALER_CONFIGURATION_0=""
  AUTOSCALER_CONFIGURATION_1=""
  AUTOSCALER_CONFIGURATION_2=""
  LOAD_PATTERN=""
  EXPERIMENT_DURATION=""
  WORKLOAD_CONFIGURATION_0=""
  WORKLOAD_CONFIGURATION_1=""
  WORKLOAD_CONFIGURATION_2=""
  WORKLOAD_CONFIGURATION_3=""
  NAMESPACE=""
  EXPERIMENT_LABEL=""
  EXPERIMENT_TAG=""
  i=0
  for w in $(echo "$line" | tr ";" "\n"); do
    if [ "$i" -eq 0 ]
    then
      QUERY="${w}"
    elif [ "$i" -eq 1 ]
    then
      MODE="${w}"
    elif [ "$i" -eq 2 ]
    then
      INITIAL_PARALLELISM="${w}"
    elif [ "$i" -eq 3 ]
    then
      AVAILABLE_TASKMANAGERS="${w}"
    elif [ "$i" -eq 4 ]
    then
      AUTOSCALER="$w"
    elif [ "$i" -eq 5 ]
    then
      AUTOSCALER_CONFIGURATION_0="${w}"
    elif [ "${i}" -eq 6 ]
    then
      AUTOSCALER_CONFIGURATION_1="${w}"
    elif [ "${i}" -eq 7 ]
    then
      AUTOSCALER_CONFIGURATION_2="${w}"
    elif [ "${i}" -eq 8 ]
    then
      LOAD_PATTERN="${w}"
    elif [ "${i}" -eq 9 ]
    then
      EXPERIMENT_DURATION="${w}"
    elif [ "${i}" -eq 10 ]
    then
      WORKLOAD_CONFIGURATION_0="${w}"
    elif [ "${i}" -eq 11 ]
    then
      WORKLOAD_CONFIGURATION_1="${w}"
        elif [ "${i}" -eq 12 ]
    then
      WORKLOAD_CONFIGURATION_2="${w}"
        elif [ "${i}" -eq 13 ]
    then
      WORKLOAD_CONFIGURATION_3="${w}"
    elif [ "${i}" -eq 14 ]
    then
      NAMESPACE="${w}"
    elif [ "${i}" -eq 15 ]
    then
      EXPERIMENT_LABEL="${w}"
    elif [ "${i}" -eq 16 ]
    then
      EXPERIMENT_TAG="${w}"
    fi
    i=$((i+1))
  done
}

function deployExperiment() {
    parseLine
    echo "Deploying experiment with
      QUERY=${QUERY}  MODE=${MODE}
      INITIAL_PARALLELISM=${INITIAL_PARALLELISM} AVAILABLE_TASKMANAGERS=${AVAILABLE_TASKMANAGERS}
      AUTOSCALER=${AUTOSCALER}[${AUTOSCALER_CONFIGURATION_0},${AUTOSCALER_CONFIGURATION_1},${AUTOSCALER_CONFIGURATION_2}]
      LOAD_PATTERN=${LOAD_PATTERN}[${EXPERIMENT_DURATION},${WORKLOAD_CONFIGURATION_0},${WORKLOAD_CONFIGURATION_1},${WORKLOAD_CONFIGURATION_2},${WORKLOAD_CONFIGURATION_3}
      NAMESPACE=${NAMESPACE}
      "

    source ./deploy_experiment.sh  \
      "${QUERY}" \
      "${MODE}" \
      "${INITIAL_PARALLELISM}" \
      "${AVAILABLE_TASKMANAGERS}" \
      "${AUTOSCALER}" \
      "${AUTOSCALER_CONFIGURATION_0}" \
      "${AUTOSCALER_CONFIGURATION_1}" \
      "${AUTOSCALER_CONFIGURATION_2}" \
      "${LOAD_PATTERN}" \
      "${EXPERIMENT_DURATION}" \
      "${WORKLOAD_CONFIGURATION_0}" \
      "${WORKLOAD_CONFIGURATION_1}" \
      "${WORKLOAD_CONFIGURATION_2}" \
      "${WORKLOAD_CONFIGURATION_3}" \
      "${NAMESPACE}"
}

function fetchExperiments() {
    parseLine

    AUTOSCALER_CONFIGURATION_NAME="${AUTOSCALER_CONFIGURATION_0},${AUTOSCALER_CONFIGURATION_1},${AUTOSCALER_CONFIGURATION_2}"
    # shellcheck disable=SC2026
    AUTOSCALER_CONFIGURATION_NAME=$(echo "${AUTOSCALER_CONFIGURATION_NAME}" | sed 's/_//'g | sed 's/,$//' | sed 's/,$//')
    if [ "${AUTOSCALER_CONFIGURATION_NAME}" == "" ]
    then
      AUTOSCALER_CONFIGURATION_NAME="-"
    fi

    echo "Fetching data from
      QUERY=${QUERY}  MODE=${MODE}
      LOAD_PATTERN=${LOAD_PATTERN}  EXPERIMENT_DURATION=${EXPERIMENT_DURATION}
      AUTOSCALER=${AUTOSCALER}  AUTOSCALER_CONFIGURATION_NAME=${AUTOSCALER_CONFIGURATION_NAME}
      EXPERIMENT_LABEL=${EXPERIMENT_LABEL}  EXPERIMENT_TAG=${EXPERIMENT_TAG}
      "

    source ./fetch_experiment_results.sh "${QUERY}" "${MODE}" "${LOAD_PATTERN}" "${EXPERIMENT_DURATION}" "${AUTOSCALER}" \
      "${AUTOSCALER_CONFIGURATION_NAME}" "${EXPERIMENT_LABEL}" "${EXPERIMENT_TAG}"
}

function undeployExperiments() {
  parseLine
  echo "Undeploying experiment with QUERY=${QUERY} MODE=${MODE} AUTOSCALER=${AUTOSCALER} NAMESPACE=${NAMESPACE}"
  source ./undeploy_experiment.sh "${QUERY}" "${MODE}" "${AUTOSCALER}" "${NAMESPACE}"
}

paste -d@ ${EXPERIMENT_FILE} | while IFS="@" read -r e0
do
  line="${e0}"

  echo "Deploying all containers"
  deployExperiment
  echo "Finished deploying all containers"

  sleep "${EXPERIMENT_DURATION}"m

  echo "Collect all data"
  fetchExperiments
  echo "Finished collecting all data."

  sleep 30s

  echo "Undeploying all containers"
  undeployExperiments
  echo "Finished undeploying all containers"

  sleep 1m
done
