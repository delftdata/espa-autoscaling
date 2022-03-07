import time
import os
import requests
import json
import math
from kubernetes import client, config
from datetime import datetime
from prometheus_client import start_http_server, Gauge

# start_http_server(8000)
# cooldown_metric = Gauge('dhalion_autoscaler_cooldown', 'amount of seconds remaining in cooldown')
# cooldown_metric.set(-1)
#
# backpressure_metric = Gauge('dhalion_autoscaler_backpressure', 'backpressure value')
# backpressure_metric.set(-1)
#
# consumer_lag_metric = Gauge('consumer_lag', 'consumer lag')
# consumer_lag_metric.set(-1)

def keep_running():
        try:
                run()
        except:
                keep_running()

def run():
        while True:
                print('Executing Dhalion Script')

                # obtain environmental variables
                cooldown = os.environ['COOLDOWN']
                avg_over_time = os.environ['AVG_OVER_TIME']
                min_replicas = int(os.environ['MIN_REPLICAS'])
                max_replicas = int(os.environ['MAX_REPLICAS'])
                sleep_time = int(os.environ['SLEEP_TIME'])
                backpressure_lower_threshold = float(os.environ['BACKPRESSURE_LOWER_THRESHOLD'])
                backpressure_upper_threshold = float(os.environ['BACKPRESSURE_UPPER_THRESHOLD'])
                cpu_lower_threshold = float(os.environ['CPU_LOWER_THRESHOLD'])
                cpu_upper_threshold = float(os.environ['CPU_UPPER_THRESHOLD'])
                consumer_lag_threshold = float(os.environ['CONSUMER_LAG_THRESHOLD'])
                scaling_factor = int(os.environ['SCALING_FACTOR_PERCENTAGE'])

                # obtain backpressure metric from prometheus
                backpressure_query = requests.get("http://prometheus-server/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[" + avg_over_time +"]))")
                backpressure_value = backpressure_query.json()["data"]["result"][0]["value"][1]
                print("backpressure value: " + str(backpressure_value))
                # backpressure_metric.set(str(backpressure_value))

                # obtain consumer lag from prometheus
                consumer_lag = requests.get("http://prometheus-server/api/v1/query?query=avg(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max)")
                consumer_lag = consumer_lag.json()["data"]["result"][0]["value"][1]
                print("consumer lag value: " + str(consumer_lag))
                # consumer_lag_metric.set(str(consumer_lag))

                # obtain cpu utilization from prometheus
                cpu_load = requests.get(
                        "http://prometheus-server/api/v1/query?query=avg(avg_over_time(flink_taskmanager_Status_JVM_CPU_Load[" + avg_over_time + "]))")
                cpu_load = cpu_load.json()["data"]["result"][0]["value"][1]
                print("cpu load value: " + str(cpu_load))


                # obtain previous scaling event
                previous_scaling_event = requests.get("http://prometheus-server/api/v1/query?query=deriv(flink_jobmanager_numRegisteredTaskManagers[" + cooldown + "])")
                previous_scaling_event = previous_scaling_event.json()["data"]["result"][0]["value"][1]
                print("taskmanager deriv: " + str(previous_scaling_event))

                # autenticate with kubernetes API
                config.load_incluster_config()
                v1 = client.AppsV1Api()

                # retrieving current number of taskmanagers from kubernetes API
                current_number_of_taskmanagers = None
                ret = v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True, field_selector="metadata.name=flink-taskmanager")
                for i in ret.items:
                        current_number_of_taskmanagers = int(i.spec.replicas)
                print("current number of taskmanagers: " + str(current_number_of_taskmanagers))


                if float(previous_scaling_event) == 0:
                        # scaling logic
                        new_number_of_taskmanagers = current_number_of_taskmanagers
                        if (float(backpressure_value) > backpressure_upper_threshold or float(cpu_upper_threshold)) and current_number_of_taskmanagers < max_replicas:
                                        if math.ceil(new_number_of_taskmanagers *  (1 + scaling_factor)) <= max_replicas:
                                                new_number_of_taskmanagers = math.ceil(new_number_of_taskmanagers*(1+scaling_factor))
                                        else:
                                                new_number_of_taskmanagers = max_replicas
                                        print("scaling up to: " + str(new_number_of_taskmanagers))
                        elif float(backpressure_value) < backpressure_lower_threshold and float(consumer_lag) < consumer_lag_threshold and current_number_of_taskmanagers > min_replicas and float(cpu_load) < cpu_lower_threshold:
                                        if math.floor(new_number_of_taskmanagers * (1 - scaling_factor)) >= min_replicas:
                                                new_number_of_taskmanagers = math.floor(new_number_of_taskmanagers * (1 - scaling_factor))
                                        else:
                                                new_number_of_taskmanagers = min_replicas

                                        print("scaling down to: " + str(new_number_of_taskmanagers))

                        # adjusting number of taskmanagers
                        if current_number_of_taskmanagers != new_number_of_taskmanagers:
                                try:
                                        body = {"spec":{"replicas":new_number_of_taskmanagers}}
                                        api_response = v1.patch_namespaced_deployment_scale(name="flink-taskmanager", namespace="default", body=body, pretty=True)
                                except Exception as e:
                                        print(e)
                        else:
                                print("not scaling due to no change")
                else:
                        print("in cooldown period")

                time.sleep(sleep_time)

if __name__ == "__main__":
    keep_running()
