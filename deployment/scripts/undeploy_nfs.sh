#!/bin/bash
# Undeploy the NFS server required for flink-jobmanager setup
# Script assumes execution from the google_cloud directory

echo "Undeploying nfs server"
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')
echo "step 1"
kubectl delete --wait=true -f nfs-first-claim.yaml
echo "step 2"
kubectl delete --wait=true -f nfs-service.yaml
echo "step 3"
envsubst < nfs-claim.yaml | kubectl delete --wait=true -f -
echo "step 4"
kubectl delete --wait=true -f nfs.yaml
echo "step 5"
echo "Finished undeploying deploying nfs server"