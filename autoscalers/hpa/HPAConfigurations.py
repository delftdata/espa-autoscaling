import os

from common import Configurations


class HPAConfigurations(Configurations):
    HPA_SCALE_DOWN_WINDOW_SECONDS = int(os.environ.get("HPA_SCALE_DOWN_WINDOW_SECONDS", 300))

    def print_configurations(self):
        super().print_configurations()
        print(f"\tHPA_SCALE_DOWN_WINDOW_SECONDS: {self.HPA_SCALE_DOWN_WINDOW_SECONDS}")
