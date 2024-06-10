# Evaluating Stream Processing Autoscalers
This repository contains the code and the data generators for the paper "Evaluating Stream Processing Autoscalers" by
George Siachamis et al., in DEBS 2024.

# Experimental setup

## Queries
Experiments are performed usign the following NexMark queries:
- Q1
- Q2
- Q3
- Q5
- Q11

All queries are adapted to use Kafka as ingress/egress.


## Auto scalers
Experiments are performed using the following auto scalers:
- DS2
- Dhalion
- HPA
- HPA-Vargas

## Deployment
Instructions on how to deploy and use the experimental framework are include in the deployment directory.

## Data processing
After deployment, data can be retrieved using the scripts found in /data_processing/. 
