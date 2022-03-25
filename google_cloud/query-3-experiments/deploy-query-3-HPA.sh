#!/bin/bash

bash deploy-query-3.sh

cd ..

cd common-files

kubectl wait --timeout=4m --for=condition=ready statefulset --all

kubectl apply -f cpu-hpa-stabelized.yaml

