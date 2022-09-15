#!/bin/bash

kubectl apply -f ./nfs/first-claim.yaml

#kubectl apply -f ./nfs/claim.yaml
kubectl apply -f ./nfs/nfs.yaml

kubectl apply -f ./nfs/nfs-service.yaml


