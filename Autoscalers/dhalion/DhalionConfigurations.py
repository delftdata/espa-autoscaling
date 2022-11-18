import os

from common import Configurations


class DhalionConfigurations(Configurations):
    # Size of the monitoring period
    DHALION_MONITORING_PERIOD_SECONDS = int(os.environ.get("DHALION_MONITORING_PERIOD_SECONDS", "360"))
    # Scale down factor
    DHALION_SCALE_DOWN_FACTOR = float(os.environ.get("DHALION_SCALE_DOWN_FACTOR", "0.8"))
    # Maximum buffersize for it to be considered 'close to zero'
    DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD = float(os.environ.get("DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD", "0.1"))

    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tDHALION_MONITORING_PERIOD_SECONDS: {self.DHALION_MONITORING_PERIOD_SECONDS}")
        print(f"\tDHALION_SCALE_DOWN_FACTOR: {self.DHALION_SCALE_DOWN_FACTOR}")
        print(f"\tDHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD: {self.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD}")

