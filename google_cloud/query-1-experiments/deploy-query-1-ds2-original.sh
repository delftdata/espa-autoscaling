#!/bin/bash



bash deploy-query-1.sh

cd ..

cd common-files

kubectl wait --timeout=3m --for=condition=ready statefulset --all
kubectl apply -f rules_ds2.yaml
kubectl apply -f ds2-deployment.yaml


