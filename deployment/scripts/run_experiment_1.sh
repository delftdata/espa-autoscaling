#!/bin/bash

echo "Deploying"
source ./scripts/deploy_nfs.sh
source ./scripts/deploy_query_1.sh
source ./scripts/deploy_autoscaler.sh

echo "Finished deploying"

bash sleep 300

echo "Undeploying"
source ./scripts/undeploy_autoscaler.sh
source ./scripts/undeploy_query_1.sh
source ./scripts/undeploy_nfs.sh

echo "Finished undeploying"
