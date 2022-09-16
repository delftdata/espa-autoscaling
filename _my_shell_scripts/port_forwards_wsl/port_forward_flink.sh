#!/bin/bash

echo "Forwarding flink to port 8081"
JOB_MANAGER_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=flink,component=jobmanager)
kubectl port-forward $JOB_MANAGER_NAME 8081
