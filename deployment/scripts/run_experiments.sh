#!/bin/bash

echo "Deploying"
source ./scripts/deploy_nfs.sh
source ./scripts/deploy_query_1.sh
source ./scripts/deploy_autoscaler.sh

echo "Finished deploying"

echo "Press any key to continue"
WAIT=true
while [ $WAIT ] ; do
  read -t 3 -n 1
  if [ $? = 0 ] ; then
    WAIT=false ;
  else
    echo "waiting for the keypress"
  fi
done

echo "Undeploying"
source ./scripts/undeploy_autoscaler.sh
source ./scripts/undeploy_query_1.sh
source ./scripts/undeploy_nfs.sh

echo "Finished undeploying"
