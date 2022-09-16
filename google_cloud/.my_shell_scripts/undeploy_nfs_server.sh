#!/bin/bash

echo "Undeploying nfs server"

export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')
kubectl delete --wait=true -f ./nfs/first-claim.yaml
kubectl delete --wait=true -f ./nfs/nfs-service.yaml
envsubst < ./nfs/claim.yaml | kubectl delete --wait=true -f -

kubectl delete --wait=true -f jobmanager-service.yaml
kubectl delete --wait=true -f ./nfs/nfs.yaml

echo "Finished undeploying deploying nfs server"