#!/bin/bash
# Undeploy the NFS server required for flink-jobmanager setup
# Script assumes execution from the google_cloud directory

echo "Undeploying nfs server"
kubectl delete pvc --all
kubectl delete pv --all
kubectl delete --wait=true -f nfs-service.yaml
kubectl delete --wait=true -f nfs.yaml
echo "Finished undeploying deploying nfs server"