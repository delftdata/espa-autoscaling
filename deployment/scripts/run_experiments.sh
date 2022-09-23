#!/bin/bash

echo "Deploying"
#source ./scripts/deploy_nfs.sh
source ./scripts/deploy_queries.sh
source ./scripts/deploy_autoscaler.sh

echo "Finished deploying"

echo "Press any key to continue"

read -p "Press any key..."

echo "Undeploying"
source ./scripts/undeploy_autoscaler.sh
source ./scripts/undeploy_queries.sh
#source ./scripts/undeploy_nfs.sh

echo "Finished undeploying"
