class Autoscalers:
    """
    Helperclass containing all possible autoscalers with their corresponding variables used by the experiments.
    """
    DHALION = "dhalion"
    DHALION_VARIABLES = [""]

    DS2 = "ds2"
    DS2_VARIABLES = [""]

    HPA_CPU = "hpa-cpu"
    HPA_CPU_VARIABLES = [""]

    HPA_VARGA = "hpa-varga"
    HPA_VARGA_VARIABLES = [""]


    @staticmethod
    def getVariablesOfAutoscaler(autoscaler) -> [str]:
        if autoscaler == Autoscalers.DHALION:
            return Autoscalers.DHALION_VARIABLES
        elif autoscaler == Autoscalers.DS2:
            return Autoscalers.DS2_VARIABLES
        elif autoscaler == Autoscalers.HPA_CPU:
            return Autoscalers.HPA_CPU_VARIABLES
        elif autoscaler == Autoscalers.HPA_VARGA:
            return Autoscalers.HPA_VARGA_VARIABLES
        else:
            print(f"Error: did not find variables belonging to {autoscaler}.")
            return []

    @staticmethod
    def getAllAutoscalers() -> [str]:
        return [
            Autoscalers.DHALION,
            Autoscalers.DS2,
            Autoscalers.HPA_CPU,
            Autoscalers.HPA_VARGA,
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

