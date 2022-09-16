# TODO tomorrow
- Find out more about kafka stream
- Deploy project (maybe ask some help for this)

# Required installations
Install java v8
Install maven
Install docker
Install minikube
Install kubectl
Install Helm

# Run application
Enable docker
```
sudo service docker start
```
Configure minikube
```
minikube ssh 'sudo ip link set docker0 promisc on'
```

navigate to shell scripts (TODO)
```
cd my_shell_scripts
```

## Deployment
Deploy setup
```
bash deploy.sh
```

Deploy workbench
```
bash deploy_workbench.sh
```
## Run jobs
Deploy run_workbench_jobs
The jobs can be configured in this script
```
bash run_workbench_jobs.sh
```

## Undeploy
Undeploy setup
```
bash undeploy.sh
```

Undeploy workbench
```
bash undeploy_workbench.sh
```











# OLD WORKROUTINE

Build reactive-mode-demo-jobs for reactive-mode of Apache Flink
### Run build_docker.sh
This does the following 
1. Build reactive-mode-demo-jobs mvn
2. Build rmetzger/flink:1.13.0-reactive-demo
3. Push to docker: rmetzger/flink:1.13.0-reactive-demo
```
. ./build_docker.sh
```




# Part 1: readme of flink reactive mode k8s demo
Disclaimer: Added at the very beginning of the project, probably not that important

### start docker
```
sudo service docker start
```

### Download flink-reactive and push to docker
```
docker build -t rmetzger/flink:1.13.0-reactive-demo .
docker push rmetzger/flink:1.13.0-reactive-demo
```

### Start minikube (first install when needed)
```
start minicube
```

### setup docker ip link
```
minikube ssh 'sudo ip link set docker0 promisc on'
```

### Optional minikube dashboard
```
minikube dashboard
```
Dashboard is now locally available at: http://127.0.0.1:44603/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/

### Install Metrics server (for autoscaler)
```
minikube addons enable metrics-server
```

### Set kubernetics namespace
```
kubectl create namespace reactive
kubectl config set-context --current --namespace=reactive
```

### Launch flink-dynamic server
```
kubectl apply -f flink-configuration-configmap.yaml
kubectl apply -f jobmanager-application.yaml
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f taskmanager-job-deployment.yaml
```

### connect to kubectl
```
kubectl proxy
```
Kubectl is at localhost:8001

### get pods
```
kubectl get pods
```
### connect to flink UI
```
kubectl port-forward flink-jobmanager-ID 8081
kubectl port-forward flink-jobmanager-5b57l 8081
```
Flink UI is at localhost:8081


### Now everything is running!

### scale manually
```

```
---

# Old ReadMe added in oktober 2021.
### flink-reactive-mode-k8s-demo
```
# start doccker
sudo service docker start


# flink-reactive demo
docker build -t rmetzger/flink:1.13.0-reactive-demo .
# publish image
docker push rmetzger/flink:1.13.0-reactive-demo


# Install minikube!
# start minikube
minikube start


# some prep
minikube ssh 'sudo ip link set docker0 promisc on'

# optional dashboard on Minikube
minikube dashboard
# dashboard on real cluster
kubectl proxy
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')


# install metrics server (needed for autoscaler)d
minikube addons enable metrics-server

kubectl create namespace reactive
kubectl config set-context --current --namespace=reactive

# launch
kubectl apply -f flink-configuration-configmap.yaml
kubectl apply -f jobmanager-application.yaml
kubectl apply -f jobmanager-rest-service.yaml
kubectl apply -f jobmanager-service.yaml
kubectl apply -f taskmanager-job-deployment.yaml

# remove
kubectl delete -f flink-configuration-configmap.yaml
kubectl delete -f jobmanager-application.yaml
kubectl delete -f jobmanager-rest-service.yaml
kubectl delete -f jobmanager-service.yaml
kubectl delete -f taskmanager-job-deployment.yaml

# connect (doesn't work?!)
kubectl proxy

# connect to Flink UI
kubectl port-forward flink-jobmanager-rp4zv 8081

# scale manually
kubectl scale --replicas=2 deployments/flink-taskmanager

# probably based on: https://www.magalix.com/blog/kafka-on-kubernetes-and-deploying-best-practice
# start zookeeper
kubectl apply -f zookeeper-service.yaml
kubectl apply -f zookeeper-deployment.yaml

# start kafka
kubectl apply -f kafka-service.yaml
kubectl apply -f kafka-deployment.yaml

# launch a container for running the data generator
kubectl run workbench --image=ubuntu:21.04 -- sleep infinity

# connect to workbench
kubectl exec --stdin --tty workbench -- bash

# prep
apt update
apt install -y maven git htop nano iputils-ping wget net-tools
git clone https://github.com/rmetzger/flink-reactive-mode-k8s-demo.git
mvn clean install

# run data generator
mvn exec:java -Dexec.mainClass="org.apache.flink.DataGen" -Dexec.args="topic 1 kafka-service:9092 [manual|cos]"

# delete workbench
kubectl delete pod workbench

# make kafka available locally:
kubectl port-forward kafka-broker0-78fb8799f7-twdf6 9092:9092


# scale automatically
kubectl autoscale deployment flink-taskmanager --min=1 --max=5 --cpu-percent=75

# remove autoscaler
kubectl delete horizontalpodautoscalers flink-taskmanager


# prometheus
kubectl port-forward prometheus-server-667df6d57c-77dms 9090
# grafana
kubectl port-forward grafana-5df66b4d87-rkd7n 3000


# scales:
# 1 taskmanager: 20000
# 2 taskamangers: 25000
# 4 taskmanagers: 45000
# 3 taskmanagers: < 50000
# 4 taskmanagers: 55000
# 
# 9 Taskmanagers: 75000
```