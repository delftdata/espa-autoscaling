import os

from common import Configurations


class DS2Configurations(Configurations):
    DS2_LAG_PROCESSING_TIME_SECONDS = int(os.environ.get('DS2_LAG_PROCESSING_TIME_SECONDS', "120"))
    DS2_INPUT_RATE_MULTIPLIER = float(os.environ.get('DS2_INPUT_RATE_MULTIPLIER', "1"))


    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tDS2_LAG_PROCESSING_TIME_SECONDS: {self.DS2_LAG_PROCESSING_TIME_SECONDS}")
        print(f"\tDS2_INPUT_RATE_MULTIPLIER: {self.DS2_INPUT_RATE_MULTIPLIER}")

