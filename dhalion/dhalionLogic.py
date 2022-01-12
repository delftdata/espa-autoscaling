import time
import os
import requests
import json
from kubernetes import client, config


while True:
        print('Looping')
        print(os.environ['COOLDOWN'])
        backpressure_query = requests.get("http://prometheus-server/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[5m]))")
        backpressure_value = backpressure_query.json()["data"]["result"][0]["value"][1]
        print("backpressure value")
        print(backpressure_value)

        config.load_incluster_config()
        v1 = client.AppsV1Api()
        print("Listing pods with their IPs:")
        ret = v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True, field_selector="metadata.name=flink-taskmanager")
        for i in ret.items:
                print(i.spec.replicas, i.metadata.namespace, i.metadata.name)

        try:
                body = {"spec":{"replicas":3}}
                api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
                print(api_response)
        except Exception as e:
                print(e)

        time.sleep(5)
        raise Exception('Exception in loop')