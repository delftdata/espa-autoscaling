import os

from hpa import HPAConfigurations


class HPAConfigurationsCPU(HPAConfigurations):
    CPU_UTILIZATION_TARGET_VALUE = float(os.environ.get("CPU_UTILIZATION_TARGET_VALUE", 0.7))

    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tCPU_UTILIZATION_TARGET_VALUE: {self.CPU_UTILIZATION_TARGET_VALUE}")

