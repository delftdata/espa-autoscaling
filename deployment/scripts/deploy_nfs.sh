#!/bin/bash

echo "Deploying NFS Server"

# Setup NFS service
kubectl apply -f nfs-first-claim.yaml
kubectl apply -f nfs-service.yaml

# Get nfs IP and claim persistent memory
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')
envsubst < nfs-claim.yaml | kubectl apply -f -

# Deploy nfs-server
kubectl apply -f nfs.yaml
kubectl wait --timeout=3m --for=condition=ready pods --all
echo "Setting persistentVolumeReclaimPolicy to Delete"
kubectl patch pv nfs -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
echo "Finished deploying NFS server"