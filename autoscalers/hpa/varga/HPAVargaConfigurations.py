import os

from hpa.HPAConfigurations import HPAConfigurations


class HPAVargaConfigurations(HPAConfigurations):
    # Target value of the utilization
    HPA_VARGA_UTILIZATION_TARGET_VALUE = float(os.environ.get(" HPA_VARGA_UTILIZATION_TARGET_VALUE", 0.7))
    # Target value of the relative lag change
    HPA_VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE = float(os.environ.get(" HPA_VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE", 1.0))

    # Minimum kafka lag rate to consider the kafka source backpressured
    HPA_VARGA_MINIMUM_KAFKA_LAG_RATE_WHEN_BACKPRESSURED_THRESHOLD = int(os.environ.get("HPA_VARGA_MINIMUM_KAFKA_LAG_RATE_WHEN_BACKPRESSURED_THRESHOLD", "1000"))

    # Period length in seconds to determine the derivative of the lag over
    HPA_VARGA_DERIVATIVE_PERIOD_SECONDS = int(os.environ.get("HPA_VARGA_DERIVATIVE_PERIOD_SECONDS", "60"))

    # Maximum increase in parallelism in one scaling operation
    HPA_VARGA_OPERATOR_MAXIMUM_PARALLELISM_INCREASE = int(os.environ.get("HPA_VARGA_OPERATOR_MAXIMUM_PARALLELISM_INCREASE", "50"))


    def print_configurations(self):
        super().print_configurations()
        print(f"\tHPA_VARGA_UTILIZATION_TARGET_VALUE: {self.HPA_VARGA_UTILIZATION_TARGET_VALUE}")
        print(f"\tHPA_VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE: {self.HPA_VARGA_RELATIVE_LAG_CHANGE_TARGET_VALUE}")
        print(f"\tHPA_VARGA_MINIMUM_KAFKA_LAG_RATE_WHEN_BACKPRESSURED_THRESHOLD: {self.HPA_VARGA_MINIMUM_KAFKA_LAG_RATE_WHEN_BACKPRESSURED_THRESHOLD}")
        print(f"\tHPA_VARGA_DERIVATIVE_PERIOD_SECONDS: {self.HPA_VARGA_DERIVATIVE_PERIOD_SECONDS}")
        print(f"\tHPA_VARGA_OPERATOR_MAXIMUM_PARALLELISM_INCREASE: {self.HPA_VARGA_OPERATOR_MAXIMUM_PARALLELISM_INCREASE}")
