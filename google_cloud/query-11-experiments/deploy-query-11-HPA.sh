#!/bin/bash


bash deploy-query-11.sh

cd ..
cd common-files

kubectl apply -f cpu-hpa-stabelized.yaml

