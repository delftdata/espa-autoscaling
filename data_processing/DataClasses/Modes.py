class Modes:
    """
    Helper-class containing all possible modes.
    """

    DEFAULT = ""
    REACTIVE = "reactive"
    NON_REACTIVE = 'non-reactive'

    @staticmethod
    def get_all_modes() -> [str]:
        return [
            Modes.DEFAULT,
            Modes.REACTIVE,
            Modes.NON_REACTIVE,
        ]

    @staticmethod
    def is_mode(mode: str) -> bool:
        return Modes.get_all_modes().__contains__(mode)

