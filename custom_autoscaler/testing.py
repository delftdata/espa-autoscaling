import os
import json
import sys
import requests
import datetime
from datetime import datetime

with open('./test_pd/cooldown.txt', 'r') as f:
    lines = f.readlines()
    f.close()


current_time = datetime.now()


old_time = lines[0]
print(old_time)
old_time_converted = datetime.strptime(old_time, "%Y-%m-%d %H:%M:%S.%f")

difference = (current_time - old_time_converted).seconds

with open('./test_pd/cooldown.txt', 'w') as f:
    f.write(str(current_time))
    f.close()

# try:
#     # Make request to Pod metric endpoint
#     # (see ../flask-metrics/ folder for simple flask app exposing this endpoint)
#     backpressure_query = requests.get(
#         "http://localhost:9090/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[5m]))")
#     outpool_query = requests.get(
#         "http://localhost:9090/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_buffers_outPoolUsage[5m]))")
#
#     backpressure_value = backpressure_query.json()["data"]["result"][0]["value"][1]
#     outpool_value = outpool_query.json()["data"]["result"][0]["value"][1]
#
#     return_value = {"backpressure": backpressure_value, "outpool": outpool_value}
#     print(return_value)
#     # Output whatever metrics are gathered to stdout
#     sys.stdout.write(str(return_value))
# except HTTPError as http_err:
#     # If an error occurs, output error to stderr and exit with status 1
#     sys.stderr.write(f"HTTP error occurred: {http_err}")
#     exit(1)
# except Exception as err:
#     # If an error occurs, output error to stderr and exit with status 1
#     sys.stderr.write(f"Other error occurred: {err}")
#     exit(1)





