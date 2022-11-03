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

### Experiment deployemnt
To deploy a full experiment, the following script can be ran: ./scripts/deploy_experiments.
This script stitches together the NFS-server deployment, the Query deployment and the Autoscaler deployment.
It requires the following paramters
* Query: query to be deployed. Possible values {1, 3, 11}
* Autoscaler: The autoscaler to be used. Possible values {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"} 
* Metric
  * dhalion: 1, 5, 10
  * ds2: 0, 33, 66
  * HPA: 50, 70, 90
  * varga: 0.3, 0.5, 0.7

```
AUTOSCALER="dhalion"
METRIC=5
QUERY=1
bash ./scripts/deploy_experiments.sh $AUTOSCALER $METRIC $QUERY
```



## Undeployment

Undeployment is structured in the same way as deployment is performed and requires the same paramters. 
Only the order in which undeployment takes place is reversed:
1. Undeploy autoscalers
2. Undeploy queries
3. Undeploy nfs-server

Please note: It is important to first fully undeploy the taskmanagers (during query unemployment) before removing the nfs server.
Undeploying the nfs server before undeploying the taskmanagers will result in a waiting loop, having the nfs volume wait 
for the taskmanagers to be deleted and the taskmanagers waiting to connect to the nfs server to correctly shutdown.
If this happens, manually forcing the taskmanagers to close and then removing the persistent nfs volume will fix the problem 

### Autoscaler undeployment
Autoscalers are undeployed by running the following script: ./scripts/undeploy_autoscalers.sh.
The script requires the following paramter: Autoscaler
* Autoscaler: autoscaler to be undeployed. Possible values: {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
```
AUTOSCALER="dhalion"
bash ./scripts/undeploy_autoscalers.sh $AUTOSCALER
```

### Query Undeployment
Queries are automatically undeployed by running the following script: ./scripts/undeploy_queries.sh.
The script requires the following parameter: query
 * Query: query to be undeployed. Possible values {1, 3, 11}

```
QUERY=1
bash ./scripts/undeploy_queries.sh $QUERY
```

### Nfs server undeployment
NFS server is automatically undeployed by running following script: ./scripts/undeploy_nfs.sh
The script does not require any paramters

```
bash ./scripts/undeploy_nfs.sh
```

### Experiment undeployemnt
To undeploy a full experiment, the following script can be ran: ./scripts/undeploy_experiments.
This script stitches together the Autoscaler undeployment, Query undeployment and NFS-server undeployment.
The scirpt requires the following parameters: query and autoscaler
 * Query: query to be undeployed. Possible values {1, 3, 11}
 * Autoscaler: autoscaler to be undeployed. Possible values: {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
```
QUERY=1
AUTOSCALER="dhalion"
bash ./scripts/undeploy_experiment.sh $QUERY $AUTOSCALER
```

## Automatic experiment deployment
