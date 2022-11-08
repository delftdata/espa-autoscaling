# How to run experiments

## Deployment

Deployment occurs in three steps:
1. NFS server deployment
2. Query deployment
3. Autoscaler deployment


:heavy_exclamation_mark: :heavy_exclamation_mark: :heavy_exclamation_mark: To run the deployment scripts you need to be in the scripts folder.
```
cd deployments/scripts
```


### NFS server deployment
The NFS server can automatically be deployed by running the ./deploy_nfs.sh script. 
The script does not require any parameter.
```
bash ./deploy_nfs.sh
```

The script does the following
1. Apply ./yamls/nfs/nfs-first-claim.yaml
2. Apply ./yamls/nfs/nfs-service.yaml
3. Apply ./yamls/nfs/nfs-claim.yaml
4. Apply ./yamls/nfs/nfs.yaml 
5. Set persistentVolumeClaim to delete

In between, the system waits a maximum of 3 minutes for everything to be ready.

### Query deployment
Queries are automatically deployed by running the ./deploy_queries.sh. 
This script requires the following parameters: Query, Mode
* Query: The query to be deployed. Possible values: {1, 3, 11}
* Mode: The mode in which the query should be deployed. Possible values: {reactive, non-reactive}

```
query=1
mode="non-reactive"
bash ./deploy_queries.sh $query $mode
```

The script does the following:

1. Deploy Flink jobmanager service
2. Deploy Flink Taskmanagers
3. Deploy Zookeeper
4. Deploy kafka multi-broker
5. Download and install Prometheus and Grafana and make them externally accessible

Then, depending on the queries and the mode, the proper:
1. Kafka topics are installed
2. Experiment jobmanager is installed
3. Experiment workbench is installed.


### Autoscaler deployement
Autoscalers are automatically deployed by running the ./deploy_autoscalers.sh.
This script requires the following parameters: Autoscalers, Metric, Query, Mode
* Autoscalers: Autoscaler to be deployed. Possible values {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
* Metric: Metric corresponding to autoscaler
  * dhalion: 1, 5, 10
  * ds2: 0, 33, 66
  * HPA: 50, 70, 90
  * varga: 0.3, 0.5, 0.7
* Query: query to be deployed. Possible values {1, 3, 11}
* Mode: The mode in which the query should be deployed. Possible values: {reactive, non-reactive}

```
AUTOSCALER="dhalion"
METRIC=5
QUERY=1
MODE="non-reactive"
bash ./deploy_autoscalers.sh $AUTOSCALER $METRIC $QUERY $MODE
```

The script does the following:
1. Deploy autoscaler pod using metric and query configuration

### Experiment deployemnt
To deploy a full experiment, the following script can be ran: ./deploy_experiments.
This script stitches together the NFS-server deployment, the Query deployment and the Autoscaler deployment.
It requires the following paramters
* Query: query to be deployed. Possible values {1, 3, 11}
* Autoscaler: The autoscaler to be used. Possible values {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"} 
* Metric
  * dhalion: 1, 5, 10
  * ds2: 0, 33, 66
  * HPA: 50, 70, 90
  * varga: 0.3, 0.5, 0.7
 * Mode: The mode in which the query should be deployed. Possible values: {reactive, non-reactive}

```
AUTOSCALER="dhalion"
METRIC=5
QUERY=1
MODE="non-reactive"
bash ./deploy_experiments.sh $AUTOSCALER $METRIC $QUERY $MODE
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
If this happens, manually forcing the taskmanagers to close and then removing the persistent nfs volume will fix the problem.

### Autoscaler undeployment
Autoscalers are undeployed by running the following script: ./undeploy_autoscalers.sh.
The script requires the following paramter: Autoscaler, Mode
* Autoscaler: autoscaler to be undeployed. Possible values: {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
* Mode: The mode in which the query should be deployed. Possible values: {reactive, non-reactive}

```
AUTOSCALER="dhalion"
MODE="non-reactive"
bash ./undeploy_autoscalers.sh $AUTOSCALER $MODE
```

### Query Undeployment
Queries are automatically undeployed by running the following script: ./undeploy_queries.sh.
The script requires the following parameter: query, mode
 * Query: query to be undeployed. Possible values {1, 3, 11}
 * Mode: The mode in which the query should be deployed. Possible values: {reactive, non-reactive}


```
QUERY=1
MODE="non-reactive"
bash ./undeploy_queries.sh $QUERY $MODE
```

### Nfs server undeployment
NFS server is automatically undeployed by running following script: ./undeploy_nfs.sh
The script does not require any paramters

```
bash ./undeploy_nfs.sh
```

### Experiment undeployemnt
To undeploy a full experiment, the following script can be ran: ./scripts/undeploy_experiments.
This script stitches together the Autoscaler undeployment, Query undeployment and NFS-server undeployment.
The scirpt requires the following parameters: query and autoscaler
 * Query: query to be undeployed. Possible values {1, 3, 11}
 * Autoscaler: autoscaler to be undeployed. Possible values: {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
 * Mode: The mode in which the query should be deployed. Possible values: {reactive, non-reactive}

```
QUERY=1
AUTOSCALER="dhalion"
MODE="non-reactive"
bash ./scripts/undeploy_experiment.sh $QUERY $AUTOSCALER $MODE
```

## Prometheus data fetch
To fetch data from the prometheus server, the following script can be ran: ./fetch_prometheus_results.sh
This script requires the following parameters: query, autoscaler, metric, run_local
* Query: query to be deployed. Possible values {1, 3, 11}
* Autoscalers: Autoscaler to be deployed. Possible values {"dhalion", "ds2-original", "ds2-updated", "HPA", "varga1", "varga2"}
* Metric: Metric corresponding to autoscaler
  * dhalion: 1, 5, 10
  * ds2: 0, 33, 66
  * HPA: 50, 70, 90
  * varga: 0.3, 0.5, 0.7
* run_local is an boolean indicating whether the kubernetes cluster is ran locally using minikube or ran in a cluster.
  * When false, a port-forward is created to be able to access the prometheus server. After this is done, the data is fetched.
  * When true, data is immediately fetched from the server
For the current experiments, run_local=false is used.

Data is fetched by running the data_processing package from the deployment directory with the correct parameters.
This runs the _process_data_ method found in data_processing/a_processing.py.
The method _process_data_ does the following
1. Scrape data from prometheus server by running the scrape_data method found in data_processing/b_scrape-data.py.
This method scrapes the data from the prometheus server and saves all metrics separately in deployment/experiment_data/individual_data
2. Combine all metrics in a single file that is stored at deployment/experiment_data/full_data. 
  This is done by running the combine_all_metrics method found in data_processing/c_combine_all_metrics.py.
3. Plot all metrics i by running the plot_experiments method found in data_processing/d_plot_experiments.py
  This file is stored in deployment/experiment_data/full_figures.
4. Plot a subset of metrics by running the plot_detailed_plot found in data_processing/e_plot_detailed_plot.py
  This file is stored in deployment/experiment_data/detailed_figures.
5. Write all evaluation metrics in a file by running the calculate_evaluation_metrics method found in data_processing/f_plot_detailed_plot.py
  This file is stored in deployment/experiment_data/evaluation_metrics.


## Automatic experiment deployment
A script to automatically deploy and undeploy experiments is in place.
This script allows for 1-3 experiments to be run in parallel and can easily be extended to multiple files.

For each batch of experiments, 2 configurations are required:
- A minikube namespace to run the experiment in. These are variable ns0, ns1, ns2 and should be a string.
Example:
```
ns0="profile-1"
```
- A list of experiment configurations to run consecutively. These are variables file0, file1, file2.
  The format of the experiment configurations is the following: {query};{autoscaler};{configuration}
  A configuration should be placed on every line. All 
Example:
```
3;dhalion;10
1;ds2-original;0
3;ds2-updated;66
11;HPA;50
1;varga1;0.7
11;varga2;0.3
```
Examples of this file are stored in the experiments folder
The system does not support an unequal amount of experiment runs per file. This scenario will likely fail.

Overall the automatic experiment deployment does the following
1. Read next line of all provided input files
2. For each input file:
   1. Switch to minikube profile
   2. Deploy experiments using ./deploy_experiment
3. Sleep 140 minutes
4. For each input file
   1. Switch to minikube profile
   2. Fetch prometheus results using ./fetch_proometheus_results.sh
5. For each input file
   1. Switch to minikube profile
   2. Undeploy experiment using ./undeploy_experiment
6. Repeat until no more lines in files


