#!/bin/bash

echo "Starting minikube"
# memory was 8092 earlier
minikube start --memory 8092 --cpus 16
minikube addons enable metrics-server
