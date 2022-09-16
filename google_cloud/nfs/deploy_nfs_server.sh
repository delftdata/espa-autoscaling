#!/bin/bash
# Deploy NFS server required for flink-jobmanager setup
# Script assumes execution from the google_cloud directory.

# Deploy nfs-service
echo "Creating nfs-server service"
kubectl apply -f ./nfs/first-claim.yaml
kubectl apply -f ./nfs/nfs-service.yaml

echo "Setting up nfs server"
# Get nfs IP and claim persistent memory
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')
envsubst < ./nfs/claim.yaml | kubectl apply -f -
# Deploy nfs-server
kubectl apply -f ./nfs/nfs.yaml

kubectl wait --timeout=3m --for=condition=ready pods --all
echo "Finished deploying nfs server"