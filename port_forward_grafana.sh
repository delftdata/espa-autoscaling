#!/bin/bash

echo "Forwarding grafana to port 3000"
JOB_MANAGER_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app.kubernetes.io/instance=grafana)
kubectl port-forward $JOB_MANAGER_NAME 3000