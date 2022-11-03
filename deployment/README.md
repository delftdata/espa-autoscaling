# How to run experiments

## Deployment

Deployment occurs in three steps:
1. NFS server deployment
2. Query deployment
3. Autoscaler deployment

### NFS server deployment
The NFS server can automatically be deployed by running the ./scripts/deploy_nfs.sh script. 
The script does not require any parameter.
```
bash ./scripts/deploy_nfs.sh
```

The script does the following
1. Apply ./nfs-first-claim.yaml
2. Apply ./nfs-service.yaml
3. Apply ./nfs-claim.yaml
4. Apply ./nfs.yaml 
5. Set persistentVolumeClaim to delete

In between, the system waits a maximum of 3 minutes for everything to be ready.

### Query deployment
Queries are automatically deployed by running the ./scripts/deploy_nfs.sh. 
This script requires the following parameters: Query
* Query: The query to be deployed. Possible values: {1, 3, 11}

```
QUERY=1
bash ./scripts/deploy_queries.sh $query
```

The script does the following:

1. Deploy Flink jobmanager service
2. Deploy Flink Taskmanagers
3. Deploy Zookeeper
4. Deploy kafka multi-broker
5. Download and install Prometheus and Grafana and make them externally accessible

Then, depending on the queries:
1. Kafka topics are installed
2. Experiment jobmanager is installed
3. Experiment workbench is installed.


### Autoscaler deployement
Autoscalers are automatically deployed by running the ./scripts/deploy_autoscalers.sh.
This script requires the following parameters: Autoscalers, Metric, QUERY
* Autoscalers: Autoscaler to be deployed. Possible values {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
* Metric: Metric corresponding to autoscaler
  * dhalion: 1, 5, 10
  * ds2: 0, 33, 66
  * HPA: 50, 70, 90
  * varga: 0.3, 0.5, 0.7
* Query: query to be deployed. Possible values {1, 3, 11}

```
AUTOSCALER="dhalion"
METRIC=5
QUERY=1
bash ./scripts/deploy_autoscalers.sh $AUTOSCALER $METRIC $QUERY
```

The script does the following:
1. Deploy autoscaler pod using metric and query configuration

## Undeployment


## Automatic experiment deployment
