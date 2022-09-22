#!/bin/bash

echo "Deploying"
bash ./scripts/deploy_nfs.sh
bash ./scripts/deploy_query_1.sh

echo "Finished deploying"
bash sleep 5

echo "Undeploying"
bash ./scripts/undeploy_query_1.sh
bash ./scripts/undeploy_nfs.sh

echo "Finished undeploying"
