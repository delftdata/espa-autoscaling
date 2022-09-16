#!/bin/bash

echo "Forwarding kafka to port 9092"
KAFKA_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" --selector=app=kafka)
kubectl port-forward $KAFKA_NAME 9092:9092
