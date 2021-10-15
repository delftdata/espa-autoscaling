#!/bin/bash

JOB_MANAGER_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=prometheus)
kubectl port-forward $JOB_MANAGER_NAME 9090

