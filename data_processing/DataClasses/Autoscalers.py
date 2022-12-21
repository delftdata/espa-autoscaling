class Autoscalers:
    """
    Helper-class containing all possible autoscalers.
    """

    DHALION = "dhalion"
    DS2 = "ds2"
    HPA_CPU = "hpa-cpu"
    HPA_VARGA = "hpa-varga"


    @staticmethod
    def getAllAutoscalers() -> [str]:
        return [
            Autoscalers.DHALION,
            Autoscalers.DS2,
            Autoscalers.HPA_CPU,
            Autoscalers.HPA_VARGA,
        ]

    @staticmethod
    def isAutoscaler(autoscaler) -> bool:
        return Autoscalers.getAllAutoscalers().__contains__(autoscaler)

