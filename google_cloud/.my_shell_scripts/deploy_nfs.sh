#!/bin/bash

# Deploy nfs-service
kubectl apply -f ./nfs/first-claim.yaml
kubectl apply -f ./nfs/nfs-service.yaml

# wait for service to load
kubectl wait --timeout=2m --for=condition=ready statefulset --all

# Get nfs IP and claim persistent memory
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')

envsubst < ./nfs/claim.yaml | kubectl apply -f -

# Deploy nfs-server
kubectl apply -f ./nfs/nfs.yaml