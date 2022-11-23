import traceback
from abc import abstractmethod
from .Configurations import Configurations

class Autoscaler:

    configurations: Configurations

    @abstractmethod
    def runAutoscalerIteration(self):
        pass

    @abstractmethod
    def setInitialMetrics(self):
        pass

    def run(self):
        """
        It first instantiates all helper classes using the provided configurations.
        Then, it initiates a never-ending loop that catches errors during the iteration and restarts the iteration.
        :return: None
        """
        print("Running autoscaler with the following configurations:")
        self.configurations.printConfigurations()

        print("Setting initial metrics for autoscaler")
        self.setInitialMetrics()

        print("Initial metrics are set successfully. Starting autoscaler")
        while True:
            try:
                self.runAutoscalerIteration()
            except KeyboardInterrupt:
                traceback.print_exc()
                return
            except:
                traceback.print_exc()
