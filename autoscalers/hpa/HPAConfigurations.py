import os

from common import Configurations


class HPAConfigurations(Configurations):
    HPA_SCALE_DOWN_WINDOW_SECONDS = int(os.environ.get("HPA_SCALE_DOWN_WINDOW_SECONDS", 300))

    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tHPA_SCALE_DOWN_WINDOW_SECONDS: {self.HPA_SCALE_DOWN_WINDOW_SECONDS}")
