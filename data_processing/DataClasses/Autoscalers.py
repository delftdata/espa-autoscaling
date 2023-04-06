class Autoscalers:
    """
    Helper-class containing all possible autoscalers.
    """
    # autoscaler_name: (title, line_color)
    autoscaler_data = {
        "dhalion": ("Dhalion", "#DB7093"),
        "ds2": ("DS2", "#6495ED"),
        "hpa-cpu": ("HPA-CPU", "#D2691E"),
        "hpa-varga": ("HPA-Varga", "#D2691E"),
    }

    @staticmethod
    def get_all_autoscalers() -> [str]:
        return list(Autoscalers.autoscaler_data.keys())

    @staticmethod
    def is_autoscaler(autoscaler) -> bool:
        return Autoscalers.get_all_autoscalers().__contains__(autoscaler.lower())

    @staticmethod
    def get_title_of_autoscaler(autoscaler: str):
        if Autoscalers.is_autoscaler(autoscaler):
            return Autoscalers.autoscaler_data[autoscaler][0]
        else:
            print(f"Error: did not recognize autoscaler {autoscaler}. Returning \"{autoscaler}\" as title instead.")
            return autoscaler

    @staticmethod
    def get_rbg_color_of_autoscaler(autoscaler: str):
        if Autoscalers.is_autoscaler(autoscaler):
            return Autoscalers.autoscaler_data[autoscaler][1]
        else:
            print(f"Error: did not recognize autoscaler {autoscaler}. Returning \"{autoscaler}\" as title instead.")
            return autoscaler
