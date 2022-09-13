# TODO tomorrow
- Find out more about kafka stream
- Deploy project (maybe ask some help for this)

# Required installations
Install java v8
Install minikube
Install Helm
Install kubectl


# Run application
Enable docker
```
sudo service docker start
```
Enable minikube
```
minikube start
```

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