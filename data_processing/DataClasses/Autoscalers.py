class Autoscalers:
    """
    Helperclass containing all possible autoscalers with their corresponding variables used by the experiments.
    """
    DHALION = "dhalion"
    DHALION_VARIABLES = ["1", "5", "10"]
    DS2_ORIGINAL = "ds2-original"
    DS2_ORIGINAL_VARIABLES = ["0", "33", "66"]
    DS2_UPDATED = "ds2-updated"
    DS2_UPDATED_VARIABLES = ["0", "33", "66"]
    HPA = "HPA"
    HPA_VARIABLES = ["50", "70", "90"]
    VARGA1 = "varga1"
    VARGA1_VARIABLES = ["0.3", "0.5", "0.7"]
    VARGA2 = "varga2"
    VARGA2_VARIABLES = ["0.3", "0.5", "0.7"]

    @staticmethod
    def getVariablesOfAutoscaler(autoscaler) -> [str]:
        if autoscaler == Autoscalers.DHALION:
            return Autoscalers.DHALION_VARIABLES
        elif autoscaler == Autoscalers.DS2_ORIGINAL:
            return Autoscalers.DS2_ORIGINAL_VARIABLES
        elif autoscaler == Autoscalers.DS2_UPDATED:
            return Autoscalers.DS2_UPDATED_VARIABLES
        elif autoscaler == Autoscalers.HPA:
            return Autoscalers.HPA_VARIABLES
        elif autoscaler == Autoscalers.VARGA1:
            return Autoscalers.VARGA1_VARIABLES
        elif autoscaler == Autoscalers.VARGA2:
            return Autoscalers.VARGA2_VARIABLES
        else:
            print(f"Error: did not find variables belonging to {autoscaler}.")
            return []

    @staticmethod
    def getAllAutoscalers() -> [str]:
        return [
            Autoscalers.DHALION,
            Autoscalers.DS2_ORIGINAL,
            Autoscalers.DS2_UPDATED,
            Autoscalers.HPA,
            Autoscalers.VARGA1,
            Autoscalers.VARGA2
        ]

    @staticmethod
    def getAllAutoscalerVariables() -> [str]:
        return list(map(lambda autoscaler: Autoscalers.getVariablesOfAutoscaler(autoscaler),
                        Autoscalers.getAllAutoscalers()))

    @staticmethod
    def getAutoscalerAndVariables() -> [(str, [str])]:
        return list(zip(Autoscalers.getAllAutoscalers(), Autoscalers.getAllAutoscalerVariables()))

    @staticmethod
    def isAutoscaler(autoscaler) -> bool:
        return Autoscalers.getAllAutoscalers().__contains__(autoscaler)

