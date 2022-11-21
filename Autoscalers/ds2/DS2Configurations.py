import os

from common import Configurations


class DS2Configurations(Configurations):
    DS2_LAG_PROCESSING_TIME_SECONDS = int(os.environ.get('DS2_LAG_PROCESSING_TIME_SECONDS', "120"))
    DS2_INPUT_RATE_MULTIPLIER = float(os.environ.get('DS2_INPUT_RATE_MULTIPLIER', "1"))

    NONREACTIVE_CONTAINER = os.environ.get("NONREACTIVE_CONTAINER", "9923/experiments:31")
    NONREACTIVE_QUERY = int(os.environ.get("NONREACTIVE_QUERY",  "1"))
    NONREACTIVE_TIME_AFTER_DELETE_JOB = int(os.environ.get("NONREACTIVE_TIME_AFTER_DELETE_JOB",  "4"))
    NONREACTIVE_TIME_AFTER_DELETE_POD = int(os.environ.get('NONREACTIVE_TIME_AFTER_DELETE_POD', "4"))
    NONREACTIVE_TIME_AFTER_SAVEPOINT = int(os.environ.get('NONREACTIVE_TIME_AFTER_SAVEPOINT', "4"))

    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tDS2_LAG_PROCESSING_TIME_SECONDS: {self.DS2_LAG_PROCESSING_TIME_SECONDS}")
        print(f"\tDS2_INPUT_RATE_MULTIPLIER: {self.DS2_INPUT_RATE_MULTIPLIER}")
        print(f"\tNONREACTIVE_TIME_AFTER_DELETE_JOB: {self.NONREACTIVE_TIME_AFTER_DELETE_JOB}")
        print(f"\tNONREACTIVE_TIME_AFTER_DELETE_POD: {self.NONREACTIVE_TIME_AFTER_DELETE_POD}")
        print(f"\tNONREACTIVE_TIME_AFTER_SAVEPOINT: {self.NONREACTIVE_TIME_AFTER_SAVEPOINT}")

