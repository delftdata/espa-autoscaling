#!/bin/bash
# Undeploy the NFS server required for flink-jobmanager setup
# Script assumes execution from the google_cloud directory

echo "Undeploying nfs server"

# Delete all pvc and pv for parallel execution
#kubectl delete pvc --all
#kubectl delete pv --all
#kubectl delete --wait=true -f nfs-service.yaml
#kubectl delete --wait=true -f nfs.yaml

# Delete only nfs's pvc's and pv's
export NFS_SERVICE_IP=$(kubectl get svc nfs-server -o yaml | grep clusterIP | awk '{print $2}')

kubectl delete --wait=true -f ../yamls/nfs/nfs.yaml
kubectl delete --wait=true -f ../yamls/nfs/nfs-service.yaml

kubectl delete --wait=true -f ../yamls/nfs/nfs-first-claim.yaml
envsubst < ../yamls/nfs/nfs-claim.yaml | kubectl delete --wait=true -f -
echo "Finished undeploying deploying nfs server"