import time
import os
import requests
import json
from kubernetes import client, config


while True:
        print('Looping')
        print(os.environ['COOLDOWN'])
        backpressure_query = requests.get("http://prometheus-server/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerS>        backpressure_value = backpressure_query.json()["data"]["result"][0]["value"][1]
        print("backpressure value")
        print(backpressure_value)

        config.load_incluster_config()
        v1 = client.AppsV1Api()
        print("Listing pods with their IPs:")
        ret = v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True, field_selector="metadata.name=flink-taskmanager")
        for i in ret.items:
                print(i.spec.replicas, i.metadata.namespace, i.metadata.name)


        time.sleep(5)
        raise Exception('Exception in loop')
