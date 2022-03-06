#!/bin/bash

cd ..

cd common-files

helm install my-release prometheus-community/prometheus-adapter

kubectl apply -f prometheus-adapter-config.yaml
kubectl apply -f adapter-deployment.yaml
kubectl apply -f varga_HPA.yaml

cd ..
cd query-1-experiments

bash deploy-query-1.sh
