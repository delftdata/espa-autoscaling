#!/bin/bash

cd ..

cd common-files

kubectl apply -f cpu-hpa-stabelized.yaml

cd ..
cd query-1-experiments

bash deploy-query-1.sh
