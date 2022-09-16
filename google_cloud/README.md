# Deployment

## Google cloud configurations
Original experiments are run on the following cluster configurations:
```
NFS server: GCP persisten disk of 10 GB
Google cloud GKE version: 1.21.6-gke.1503
Node type: e2-standard-4 (4 vcPU, 16 GB memory)
Number of nodes: 4
Apache Kafka version: 2.7.0
Apache Flink version: 1.14.3
Zookeeper version: 3.4.10
Prometheus version: 2.34.0
Prometheus adapter version: 0.9.1
```

## Deployment
Deployment scripts can be found in the following folders:
{ query-1-experiments, query-3-experiments, query-11-experiments/ } 
In these folders, experiments can be run by executing the following script:

```
deploy-query-<query_nr>-<autoscaler>.sh
```
The scripts set up the kubernetes cluster and start the experiments.
Results can be observed on the external_grafana pod on port 3000.

## Deployment setup
When running experiments, three scripts are executed
1. The autoscaler-experiment script found at /query-<query_nr>-experiments/deploy-query-<query_nr>-<autoscaler>.sh
2. The general experiment script found at /query-<query_nr>-experiments/deploy-query-<query_nr>.sh
3. The nfs-server script found at /nfs/deploy_nfs_serer.sh

### Auto-scaler experiment script
The autoscaler-experiment script does the following
1. It runs the general experiments script, to setup most of the experiment environment
2. It deploys the auto scaler

### General experiment script
The general experiment script doe sthe following
1. It first runs the nfs-server script
2. It deploys most of the containers required by the experiment. These include

### NFS Server script
The NFS-server script does the following
1. It sets  up an NFS server for storing the checkpoints and savepoints of the Flink Jobmanagers and taskmanagers. 

TODO: extend description and include the containers used.

[//]: # (## Old comments)
[//]: # (kubectl expose deployment hello-world --type=LoadBalancer --name=my-service)
[//]: # (exposing service to internet)
[//]: # ()
[//]: # (kubectl label nodes <your-node-name> <label>)
[//]: # ()
[//]: # (constant mode:)
[//]: # (mvn exec:java -Dexec.mainClass="ch.ethz.systems.strymon.ds2.flink.nexmark.sources.BidSourceFunctionGeneratorKafka" -Dexec.args="--mode 0 --rate 200000")