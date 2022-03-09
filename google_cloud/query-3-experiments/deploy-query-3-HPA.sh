#!/bin/bash


bash deploy-query-3.sh

cd ..
cd common-files

kubectl apply -f cpu-hpa-stabelized.yaml

