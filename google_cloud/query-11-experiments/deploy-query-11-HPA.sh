#!/bin/bash

cd ..

cd common-files

kubectl apply -f cpu-hpa-stabelized.yaml

cd ..
cd query-11-experiments

bash deploy-query-11.sh
