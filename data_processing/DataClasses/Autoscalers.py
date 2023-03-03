class Autoscalers:
    """
    Helper-class containing all possible autoscalers.
    """
    # autoscaler_name: (title, line_color)
    autoscaler_data = {
        "dhalion": ("Dhalion", "#DB7093"),
        "dhalion(0.8)": ("Dhalion", "#DB7093"),
        "ds2": ("DS2", "#6495ED"),
        "ds2(1.2)": ("DS2", "#6495ED"),
        "hpa-cpu": ("HPA-CPU", "#D2691E"),
        "hpa-cpu(0.7)": ("HPA-CPU", "#D2691E"),
        "hpa-varga": ("HPA-Varga", "#49BEAA"),
        "hpa-varga(0.7)": ("HPA-Varga", "#49BEAA"),
    }

    @staticmethod
    def get_autoscaler_class(autoscaler: str):
        return autoscaler.lower().split("(")[0]

    @staticmethod
    def get_auto_scaler_label(autoscaler: str):
        autoscaler_label = Autoscalers.get_autoscaler_class(autoscaler)
        return autoscaler.replace(autoscaler_label, "", 1)

    @staticmethod
    def get_all_autoscalers() -> [str]:
        return list(Autoscalers.autoscaler_data.keys())

    @staticmethod
    def is_autoscaler(autoscaler) -> bool:
        return Autoscalers.get_all_autoscalers().__contains__(autoscaler.lower())

    @staticmethod
    def get_title_of_autoscaler(autoscaler: str):
        autoscaler_class = Autoscalers.get_autoscaler_class(autoscaler)
        if Autoscalers.is_autoscaler(autoscaler_class):
            if autoscaler in Autoscalers.autoscaler_data.keys():
                # If title of specific auto-scaler configuration is defined, return that one
                return Autoscalers.autoscaler_data[autoscaler][0]
            else:
                # Else take default auto-scaler class title and add the label of the auto-scaler.
                auto_scaler_label = Autoscalers.get_auto_scaler_label(autoscaler)
                autoscaler_title = Autoscalers.autoscaler_data[autoscaler_class][0]
                return f"{autoscaler_title}{auto_scaler_label}"
        else:
            print(f"Error: did not recognize autoscaler {autoscaler_class}. Returning \"{autoscaler}\" as title instead.")
            return autoscaler

    @staticmethod
    def get_rbg_color_of_autoscaler(autoscaler: str):
        autoscaler_class = Autoscalers.get_autoscaler_class(autoscaler)
        if Autoscalers.is_autoscaler(autoscaler_class):
            if autoscaler in Autoscalers.autoscaler_data.keys():
                # If data for the specific auto-scaler implementation is defined, return that one
                return Autoscalers.autoscaler_data[autoscaler][1]
            else:
                # Else return default color of auto-scaler class
                return Autoscalers.autoscaler_data[autoscaler_class][1]
        else:
            default_color = "#696969"
            print(f"Error: did not recognize autoscaler {autoscaler_class}. Returning {default_color} as color instead.")
            return default_color
