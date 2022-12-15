import sys
import time
import traceback

from common import Autoscaler
from dhalion import Dhalion
from hpa import HPACPU
from hpa import HPAVarga
from ds2 import DS2


def getAutoscaler(autoscaler: str) -> Autoscaler:
    print(f"Getting autoscaler: '{autoscaler}'")
    if autoscaler.lower() == "dhalion":
        return Dhalion()
    elif autoscaler.lower() == "hpa-cpu":
        return HPACPU()
    elif autoscaler.lower() == "hpa-varga":
        return HPAVarga()
    elif autoscaler.lower() == "ds2":
        return DS2()
    else:
        raise Exception(f"Error: autoscaler '{autoscaler}' not recognized.")


def setAutoscalerDeveloperConfigurations(autoscaler: Autoscaler):
    autoscaler.configurations.RUN_LOCALLY = True
    autoscaler.configurations.USE_FLINK_REACTIVE = False
    autoscaler.configurations.PROMETHEUS_SERVER = "34.91.248.224" + ":9090"
    autoscaler.configurations.FLINK_JOBMANAGER_SERVER = "35.204.243.153" + ":8081"
    autoscaler.configurations.ITERATION_PERIOD_SECONDS = 10


if __name__ == "__main__":

    developerModus = False
    if len(sys.argv) > 1:
        autoscalerName = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2] == "enable-dev":
            print("Developer mode enabled.")
            developerModus = True
    else:
        raise Exception("fError: missing argument. Please provide autoscaler as parameter {dhalion, hpa-cpu, hpa-varga}")

    maxInitializationAttempts = 5 if not developerModus else 1
    for i in range(1, maxInitializationAttempts + 1):
        try:
            print(f"Instantiating autoscaler {autoscalerName}.")
            autoscaler = getAutoscaler(autoscalerName)
            if developerModus:
                setAutoscalerDeveloperConfigurations(autoscaler)
            print(f"Autoscaler {autoscalerName} successfully instantiated.")
            autoscaler.run()
        except:
            print(f"Initialization of HPA failed ({i}/{maxInitializationAttempts}).")
            traceback.print_exc()
            time.sleep(10)
    print("Maximum amount of initialization tries exceeded. Shutting down autoscaler.")
