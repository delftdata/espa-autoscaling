import os

from common import Configurations


class DhalionConfigurations(Configurations):
    # Scale down factor
    DHALION_SCALE_DOWN_FACTOR = float(os.environ.get("DHALION_SCALE_DOWN_FACTOR", "0.8"))
    # Maximum increase in parallelism in one scaling operation
    DHALION_OPERATOR_MAXIMUM_PARALLELISM_INCREASE = int(os.environ.get("DHALION_OPERATOR_MAXIMUM_PARALLELISM_INCREASE", "50"))

    # Minimum kafka lag rate to consider the kafka source backpressured
    DHALION_KAFKA_LAG_RATE_TO_BE_BACKPRESSURED_THRESHOLD = int(os.environ.get(
        "DHALION_MINIMUM_KAFKA_LAG_RATE_WHEN_BACKPRESSURED_THRESHOLD", "1000"))

    # Maximum kafka-lag for it to be considered 'close to zero'
    DHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD = int(os.environ.get("DHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD", "10000"))
    # Maximum buffersize for it to be considered 'close to zero'
    DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD = float(os.environ.get("DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD",
                                                                        "0.2"))


    def printConfigurations(self):
        super().printConfigurations()
        print(f"\tDHALION_SCALE_DOWN_FACTOR: {self.DHALION_SCALE_DOWN_FACTOR}")
        print(f"\tDHALION_OPERATOR_MAXIMUM_PARALLELISM_INCREASE: {self.DHALION_OPERATOR_MAXIMUM_PARALLELISM_INCREASE}")
        print(f"\tDHALION_KAFKA_LAG_RATE_TO_BE_BACKPRESSURED_THRESHOLD: {self.DHALION_KAFKA_LAG_RATE_TO_BE_BACKPRESSURED_THRESHOLD}")
        print(f"\tDHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD: {self.DHALION_KAFKA_LAG_CLOSE_TO_ZERO_THRESHOLD}")
        print(f"\tDHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD: {self.DHALION_BUFFER_USAGE_CLOSE_TO_ZERO_THRESHOLD}")
