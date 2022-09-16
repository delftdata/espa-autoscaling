#!/bin/bash

echo "Undeploying workbench"

kubectl delete --wait=true pod workbench

echo "Finished undeploying workbench"
