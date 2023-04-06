import os

from hpa.HPAConfigurations import HPAConfigurations


class HPACPUConfigurations(HPAConfigurations):
    CPU_UTILIZATION_TARGET_VALUE = float(os.environ.get("CPU_UTILIZATION_TARGET_VALUE", 0.7))

    def print_configurations(self):
        super().print_configurations()
        print(f"\tCPU_UTILIZATION_TARGET_VALUE: {self.CPU_UTILIZATION_TARGET_VALUE}")
