#!/bin/bash


kubectl apply -f ./nfs/first-claim.yaml

kubectl apply -f ./nfs/nfs-service.yaml

# Now get the IP of nfs-service and add it to claim
kubectl get svc
nano ./nfs/claim.yaml

NFS_SERVICE_IP=

kubectl apply -f ./nfs/claim.yaml
kubectl apply -f ./nfs/nfs.yaml



