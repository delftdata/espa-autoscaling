#!/bin/bash

cd ..

cd common-files

kubectl apply -f dhalion_rbac_rules.yaml
kubectl apply -f dhalion-service.yaml
kubectl apply -f dhalion-deployment.yaml

cd ..
cd query-1-experiments

bash deploy-query-1.sh
