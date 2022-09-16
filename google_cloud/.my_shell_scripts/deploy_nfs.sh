#!/bin/bash

# Deploy nfs-service
echo "Creating nfs-server service"
kubectl apply -f ./nfs/first-claim.yaml
kubectl apply -f ./nfs/nfs-service.yaml


# wait for service to load
echo "Waiting for nfs-server service to be ready"
kubectl wait --timeout=3m --for=condition=ready pods --all

# Get nfs IP and claim persistent memory
echo "Setting up nfs server"
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')
envsubst < ./nfs/claim.yaml | kubectl apply -f -

# Deploy nfs-server
kubectl apply -f ./nfs/nfs.yaml