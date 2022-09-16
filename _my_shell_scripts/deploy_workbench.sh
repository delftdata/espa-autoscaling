#!/bin/bash

echo "Deploying workbench"

kubectl run workbench --image ubuntu -- sleep infinity

echo "Waiting for workbench to be ready"
  kubectl wait --timeout=5m --for=condition=ready pods --all

echo "Fetching jobs"
kubectl exec workbench -- bash -c "
  apt update &&
  apt install -y maven git htop iputils-ping wget net-tools &&
  git clone https://github.com/Jobkanis/PASAF.git &&
  cd PASAF &&
  git checkout deploy
"

echo "Building jobs"
# Install reactive-mode-demo-jobs
kubectl exec workbench -- bash -c "cd PASAF/reactive-mode-demo-jobs && mvn clean install"
# Install experiment jobs
kubectl exec workbench -- bash -c "cd PASAF/experiments && mvn clean install"

echo "Finished workbench deployment"