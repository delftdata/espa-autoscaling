
# Experiments
## Minikube deploy experiments 1 nodes vs 4 nodes
```
minikube start -p autoscaling-1n --cpus=16 --memory=64000 --nodes 1
minikube addons -p autoscaling-1n enable metrics-server

minikube start -p autoscaling-4n --cpus=4 --memory=16000 --nodes 4
minikube addons -p autoscaling-4n enable metrics-server
```
### Configure run_parallel_experiments.sh scripts
### Run run_parallel_experiments.sh script
```
nohup ./scripts/run_parallel_experiments.sh > run1.out 2>  run1.err < /dev/null &
```

### Delete minikube profiles
```
minikube delete -p autoscaling-1n
minikube delete -p autoscaling-4n
kill -9 2927287
```




Build workbench
```
docker build ./  --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/docker_rsa)"
docker build ./ --no-cache  --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/docker_rsa)"
docker build ./ --no-cache  --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/docker_rsa)" --tag jobkanis/workbench:2
```

Upload workbench to docker repository
```
docker tag {image} jobkanis/workbench:2
docker image push jobkanis/workbench:2
```

Run experiment script
```
bash ./scripts/run-experiments.sh &
```
Stop experiment running
```
ps -aux run-experiments.sh
killall run-experiments.sh inotifywait
```
Connect to tudelft server
```
ssh jkanis@student-linux.tudelft.nl
```
Pass through deployment scripts
(from https://unix.stackexchange.com/questions/174028/killing-a-shell-script-running-in-background)
```
scp -r ./deployment/ jkanis@student-linux.tudelft.nl:~/deployment
scp -r ./deployment/ jkanis@st2.ewi.tudelft.nl:~/deployment
killall `ps -aux | grep script_name | grep -v grep | awk '{ print $1 }'` && killall inotifywait
```

Move results back
```
scp -r ~/deployment/experiment_data jkanis@student-linux.tudelft.nl:~/experiment_data
scp -r jkanis@student-linux.tudelft.nl:~/experiment_data ./results/st2/
```

Run Bash
```
exec bash
```

Set profile Minikube
```
minikube profile list
minikube profile autoscalling
```





Deploy Minikube
```
minikube start -p autoscalling-q1 --cpus=16 --memory=8092

minikube start -p autoscaling-q1 --cpus=16 --memory=8092
minikube addons -p autoscaling-q1 enable metrics-server 

minikube start -p autoscaling-q2 --cpus=16 --memory=8092
minikube addons -p autoscaling-q2 enable metrics-server 

minikube start -p autoscaling-q3 --cpus=16 --memory=8092

minikube addons enable metrics-server

minikube start -p autoscaling-q3 --cpus=4 --memory=16000 --nodes 4
minikube addons -p autoscaling-q3 enable metrics-server

minikube delete -p autoscaling-q1
minikube delete -p autoscaling-q2
minikube delete -p autoscaling-q3
``````

Undeploy minikube
```
minikube stop -p autoscalling
minikube delete -p autoscalling
```

##############################
## Custom commands.md
##############################

# load gcloud
```
gcloud auth login jobkanis@gmail.com
gcloud cloud-shell ssh --authorize-session
```
# authorise
```
gcloud container clusters get-credentials pasaf-experiments --region europe-west4-a --project sigma-outlook-362608
```

# Create cluster
```
gcloud container clusters create pasaf-experiments --zone europe-west4-a --machine-type "e2-standard-8" --num-nodes=3 --disk-size=100
gcloud container clusters create pasaf-experiments --zone europe-west4-a --machine-type "e2-standard-4" --num-nodes=4 --disk-size=100
```

# Delete cluster
```
gcloud container clusters delete pasaf-experiments --zone europe-west4-a
```

#############################
# Google Cloud
#############################

Run .sh script
* Start screen session
```
screen
```
* Execute script
* Type control + a followed by control + d to disconnect screen session
* Leave server running

Stop .sh script
* Reconnect with screen
```
screen -x
```
* Stop .sh script
* Stop screen session
```
exit
```


