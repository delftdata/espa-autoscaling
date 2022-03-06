#!/bin/bash

cd ..

cd common-files

kubectl apply -f cpu-hpa-stabelized.yaml

cd ..
cd query-3-experiments

bash deploy-query-3.sh
