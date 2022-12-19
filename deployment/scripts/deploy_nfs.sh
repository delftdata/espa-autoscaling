#!/bin/bash

echo "Deploying NFS Server"

NAMESPACE=$1

# Setup NFS service
kubectl apply -f ../yamls/nfs/nfs-first-claim.yaml
kubectl apply -f ../yamls/nfs/nfs-service.yaml

# Get nfs IP and claim persistent memory
export NAMESPACE="$NAMESPACE"
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')
envsubst < ../yamls/nfs/nfs-claim.yaml | kubectl apply -f -

# Deploy nfs-server
kubectl apply -f ../yamls/nfs/nfs.yaml
kubectl wait --timeout=3m --for=condition=ready pods --all
echo "Setting persistentVolumeReclaimPolicy to Delete"
kubectl patch pv $NAMESPACE-nfs -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
echo "Finished deploying NFS server"