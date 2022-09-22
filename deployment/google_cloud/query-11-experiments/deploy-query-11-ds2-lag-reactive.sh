#!/bin/bash

bash deploy-query-11.sh

cd ..

cd common-files

kubectl wait --timeout=4m --for=condition=ready statefulset --all

kubectl apply -f rules_ds2.yaml
kubectl apply -f ds2-updated-reactive.yaml


