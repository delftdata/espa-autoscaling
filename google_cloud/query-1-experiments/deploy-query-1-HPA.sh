#!/bin/bash


bash deploy-query-1.sh

cd ..
cd common-files

kubectl apply -f cpu-hpa-stabelized.yaml

