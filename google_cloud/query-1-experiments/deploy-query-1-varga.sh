#!/bin/bash

cd ..

cd common-files


helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install my-release prometheus-community/prometheus-adapter
kubectl delete deployment/my-release-prometheus-adapter

kubectl apply -f prometheus-adapter-config_varga_v2.yaml
kubectl apply -f adapter-deployment.yaml
kubectl apply -f varga_HPA.yaml

cd ..
cd query-1-experiments

bash deploy-query-1.sh
