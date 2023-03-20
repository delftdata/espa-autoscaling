import os

from common import Configurations


class DS2Configurations(Configurations):

    # Maximum value the busy_time metric can reach. The busy time used for determining the true processing rates uses the percentage of
    # the current busy time and the maximum busy time. Default is set to 1.0.
    DS2_MAXIMUM_BUSY_TIME = float(os.environ.get("DS2_MAXIMUM_BUSY_TIME", "1.0"))

    def print_configurations(self):
        super().print_configurations()
        print(f"\tDS2_MAXIMUM_BUSY_TIME: {self.DS2_MAXIMUM_BUSY_TIME}")

