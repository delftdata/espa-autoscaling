import os

from hpa.HPAConfigurations import HPAConfigurations


class HPAConfigurationsVarga(HPAConfigurations):
    VARGA_UTILIZATION_TARGET_VALUE = float(os.environ.get("VARGA_UTILIZATION_TARGET_VALUE", 0.7))
    VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE = float(os.environ.get("VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE", 1.0))

    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tVARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE: {self.VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE}")
        print(f"\tVARGA_UTILIZATION_TARGET_VALUE: {self.VARGA_UTILIZATION_TARGET_VALUE}")
