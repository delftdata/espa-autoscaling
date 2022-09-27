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
ssh jkanis@st2.ewi.tudelft.nl
```
Pass through deployment scripts
(from https://unix.stackexchange.com/questions/174028/killing-a-shell-script-running-in-background)
```
scp -r ./deployment/ jkanis@student-linux.tudelft.nl:~/deployment
scp -r ./deployment/ jkanis@st2.ewi.tudelft.nl:~/deployment
killall `ps -aux | grep script_name | grep -v grep | awk '{ print $1 }'` && killall inotifywait
```

Run Bash
```
exec bash
```

Deploy minikube
```
minikube start --memory 8092 --cpus 16
minikube addons enable metrics-server
```

##############################
## Custom commands.md
##############################

# load gcloud
gcloud auth login jobkanis@gmail.com
gcloud cloud-shell ssh --authorize-session

# authorise
gcloud container clusters get-credentials pasaf-experiments --region europe-west4-a --project sigma-outlook-362608

# Create cluster
gcloud container clusters create pasaf-experiments --zone europe-west4-a --machine-type "e2-standard-8" --num-nodes=3 --disk-size=100
gcloud container clusters create pasaf-experiments --zone europe-west4-a --machine-type "e2-standard-4" --num-nodes=4 --disk-size=100

# Delete cluster
gcloud container clusters delete pasaf-experiments --zone europe-west4-a


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
* Stop .sh scripot
* Stop screen sessoin
```
exit
```


