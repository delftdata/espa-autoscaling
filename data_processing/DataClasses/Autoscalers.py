class Autoscalers:
    """
    Helper-class containing all possible autoscalers.
    """

    DHALION = "dhalion"
    DS2 = "ds2"
    HPA_CPU = "hpa-cpu"
    HPA_VARGA = "hpa-varga"


    @staticmethod
    def get_all_autoscalers() -> [str]:
        return [
            Autoscalers.DHALION,
            Autoscalers.DS2,
            Autoscalers.HPA_CPU,
            Autoscalers.HPA_VARGA,
        ]

    @staticmethod
    def is_autoscaler(autoscaler) -> bool:
        return Autoscalers.get_all_autoscalers().__contains__(autoscaler)

