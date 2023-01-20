#!/bin/bash
# Undeploy the NFS server required for flink-jobmanager setup
# Script assumes execution from the google_cloud directory

echo "Undeploying nfs server"

NAMESPACE=${1}

# Delete only nfs's pvc's and pv's
export NAMESPACE=${NAMESPACE}
NFS_SERVICE_IP="$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')"
export NFS_SERVICE_IP="${NFS_SERVICE_IP}"

kubectl delete --wait=true -f ../yamls/nfs/nfs.yaml
kubectl delete --wait=true -f ../yamls/nfs/nfs-service.yaml

kubectl delete --wait=true -f ../yamls/nfs/nfs-first-claim.yaml
envsubst < ../yamls/nfs/nfs-claim.yaml | kubectl delete --wait=true -f -
echo "Finished undeploying deploying nfs server"