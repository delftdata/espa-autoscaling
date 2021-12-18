import os
import json
import sys
import requests

def main():
    # Parse spec into a dict
    spec = json.loads(sys.stdin.read())
    metric(spec)

def metric(spec):
    # Get Pod IP
    try:
        # Make request to Pod metric endpoint
        # (see ../flask-metrics/ folder for simple flask app exposing this endpoint)
        backpressure_query = requests.get("http://prometheus-server/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_backPressuredTimeMsPerSecond[5m]))")
        outpool_query = requests.get("http://prometheus-server/api/v1/query?query=max(avg_over_time(flink_taskmanager_job_task_buffers_outPoolUsage[5m]))")

        backpressure_value = backpressure_query.json()["data"]["result"][0]["value"][1]
        outpool_value = outpool_query.json()["data"]["result"][0]["value"][1]

        return_value = {"backpressure": backpressure_value, "outpool": outpool_value}

        # Output whatever metrics are gathered to stdout
        sys.stdout.write(str(return_value))
    except HTTPError as http_err:
        # If an error occurs, output error to stderr and exit with status 1
        sys.stderr.write(f"HTTP error occurred: {http_err}")
        exit(1)
    except Exception as err:
        # If an error occurs, output error to stderr and exit with status 1
        sys.stderr.write(f"Other error occurred: {err}")
        exit(1)

if __name__ == "__main__":
    main()