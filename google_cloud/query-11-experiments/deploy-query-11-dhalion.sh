#!/bin/bash

bash deploy-query-3.sh

cd ..

cd common-files

kubectl wait --timeout=4m --for=condition=ready statefulset --all

kubectl apply -f dhalion_rbac_rules.yaml
kubectl apply -f dhalion-deployment_v2.yaml


