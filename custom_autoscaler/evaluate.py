# Copyright 2020 The Custom Pod Autoscaler Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import math

# JSON piped into this script example:
# {
#   "metrics": [
#     {
#       "resource": "flask-metric-869879868f-jgbg4",
#       "value": "{\"value\": 0, \"available\": 5, \"min\": 0, \"max\": 5}"
#     }
#   ],
#   "resource": {
#     "kind": "Deployment",
#     "apiVersion": "apps/v1",
#     "metadata": {
#       "name": "flask-metric",
#       "namespace": "default",
#     },
#     ...
#   },
#   "runType": "api"
# }

def main():
    # Parse JSON into a dict
    spec = json.loads(sys.stdin.read())
    evaluate(spec)

def evaluate(spec):

    metrics = spec["metrics"]


    json_value = json.loads(metrics[0]["value"])
    backpressure = float(json_value["backpressure"])
    outpool = float(json_value["outpool"])

    current_replicas = int(spec["resource"]["spec"]["replicas"])

    f = open("logs.txt", "a")
    f.write("backpressure: " + str(backpressure) + " outpool: " + str(outpool) + " current replicas:" + str(current_replicas) + "\n")

    if backpressure >= 500:
        current_replicas += 1
        f.write("scaling up \n")
    elif backpressure < 100 and outpool < 0.4:
        current_replicas -= 1
        f.write("scaling down \n")
    if current_replicas == 0:
        current_replicas = 1
        f.write("replicas = " + str(current_replicas) + "\n")
    elif current_replicas == 5:
        current_replicas = 4
        f.write("replicas = " + str(current_replicas) + "\n")

    f.close()
    

    evaluation = {}
    evaluation["targetReplicas"] = current_replicas

    # Output JSON to stdout
    sys.stdout.write(json.dumps(evaluation))

if __name__ == "__main__":
    main()