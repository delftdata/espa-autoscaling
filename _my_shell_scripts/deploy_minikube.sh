#!/bin/bash

echo "Starting minikube"
# memory was 8092 earlier
minikube start --memory 3800 --cpus 4
minikube addons enable metrics-server
