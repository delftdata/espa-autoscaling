import time
import os
import requests
import json
from kubernetes import client, config
from datetime import datetime
from prometheus_client import start_http_server, Gauge

start_http_server(8000)
cooldown_metric = Gauge('dhalion_autoscaler_cooldown', 'amount of seconds remaining in cooldown')
cooldown_metric.set(-1)

backpressure_metric = Gauge('dhalion_autoscaler_backpressure', 'backpressure value')
backpressure_metric.set(-1)

deriv_consumer_lag_metric = Gauge('dhalion_autoscaler_derivative_consumer_lag', 'derivative of consumer lag')
deriv_consumer_lag_metric.set(-1)

while True:
        print('Executing Dhalion Script')

        # obtain environmental variables
        cooldown = int(os.environ['COOLDOWN'])
        avg_over_time = os.environ['AVG_OVER_TIME']
        min_replicas = int(os.environ['MIN_REPLICAS'])
        max_replicas = int(os.environ['MAX_REPLICAS'])
        sleep_time = int(os.environ['SLEEP_TIME'])
        backpressure_lower_threshold = float(os.environ['BACKPRESSURE_LOWER_THRESHOLD'])
        backpressure_upper_threshold = float(os.environ['BACKPRESSURE_UPPER_THRESHOLD'])
        deriv_consumer_lag_threshold = float(os.environ['DERIV_CONSUMER_LAG_THRESHOLD'])

        # obtain backpressure metric from prometheus
        backpressure_query = requests.get("http://prometheus-server/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[" + avg_over_time +"]))")
        backpressure_value = backpressure_query.json()["data"]["result"][0]["value"][1]
        print("backpressure value: " + str(backpressure_value))
        backpressure_metric.set(str(backpressure_value))

        # obtain derivative of consumer lag from prometheus
        deriv_consumer_lag_query = requests.get("http://prometheus-server/api/v1/query?query=deriv(flink_taskmanager_job_task_operator_KafkaConsumer_records_lag_max[" + avg_over_time +"])")
        deriv_consumer_lag_value = deriv_consumer_lag_query.json()["data"]["result"][0]["value"][1]
        print("derivative consumer lag value: " + str(deriv_consumer_lag_value))
        deriv_consumer_lag_metric.set(str(deriv_consumer_lag_value))

        # autenticate with kubernetes API
        config.load_incluster_config()
        v1 = client.AppsV1Api()

        # retrieving current number of taskmanagers from kubernetes API
        current_number_of_taskmanagers = None
        ret = v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True, field_selector="metadata.name=flink-taskmanager")
        for i in ret.items:
                current_number_of_taskmanagers = int(i.spec.replicas)
        print("current number of taskmanagers: " + str(current_number_of_taskmanagers))

        # check when previous scaling event was
        cooldown_period_over = False
        current_time = datetime.now()
        new_cooldown_time = None

        with open('./test-pd/cooldown.txt', 'r') as f:
                last_scale_event_time = f.readlines()
                f.close()
        last_scale_event_time = last_scale_event_time[0].replace("\n", "")
        last_scale_event_time = datetime.strptime(last_scale_event_time, "%Y-%m-%d %H:%M:%S.%f")
        difference = (current_time - last_scale_event_time).seconds
        if difference > cooldown:
                        cooldown_period_over = True
                        cooldown_metric.set(0)
        else:
                        cooldown_period_over = False
                        cooldown_metric.set(str(cooldown - difference))


        if cooldown_period_over:
                # scaling logic
                new_number_of_taskmanagers = current_number_of_taskmanagers
                if float(backpressure_value) > backpressure_upper_threshold and current_number_of_taskmanagers < max_replicas:
                                new_number_of_taskmanagers += 1
                                print("scaling up to: " + str(new_number_of_taskmanagers))
                elif float(backpressure_value) < backpressure_lower_threshold and float(deriv_consumer_lag_value) < deriv_consumer_lag_threshold and current_number_of_taskmanagers > min_replicas:
                                new_number_of_taskmanagers -= 1
                                print("scaling down to: " + str(new_number_of_taskmanagers))

                # adjusting number of taskmanagers
                if current_number_of_taskmanagers != new_number_of_taskmanagers:
                        try:
                                body = {"spec":{"replicas":new_number_of_taskmanagers}}
                                api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
                                new_cooldown_time = str(datetime.now())
                                with open('./test-pd/cooldown.txt', 'w') as f:
                                        f.write(new_cooldown_time)
                                        f.close()
                        except Exception as e:
                                print(e)
                else:
                        print("not scaling due to no change")
        else:
                print("in cooldown period")

        time.sleep(sleep_time)