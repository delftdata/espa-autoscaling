#!/bin/bash

echo "Deploying"
source ./scripts/deploy_nfs.sh
source ./scripts/deploy_queries.sh
source ./scripts/deploy_autoscaler.sh dhalion 05



echo "Undeploying"
source ./scripts/undeploy_autoscaler.sh

source ./scripts/undeploy_queries.sh
source ./scripts/undeploy_nfs.sh

echo "Finished undeploying"
