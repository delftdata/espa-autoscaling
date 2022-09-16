#!/bin/bash

echo "Forwarding prometheus to port 9090"
JOB_MANAGER_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)
kubectl port-forward $JOB_MANAGER_NAME 9090