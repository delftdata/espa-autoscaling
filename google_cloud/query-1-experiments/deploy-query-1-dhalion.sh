#!/bin/bash



bash deploy-query-1.sh

cd ..

cd common-files

kubectl apply -f dhalion_rbac_rules.yaml
kubectl apply -f dhalion-deployment_v2.yaml


