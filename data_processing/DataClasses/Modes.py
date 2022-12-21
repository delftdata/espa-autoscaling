class Modes:
    """
    Helper-class containing all possible modes.
    """

    DEFAULT = ""
    REACTIVE = "reactive"
    NON_REACTIVE = 'non-reactive'

    @staticmethod
    def getAllModes() -> [str]:
        return [
            Modes.DEFAULT,
            Modes.REACTIVE,
            Modes.NON_REACTIVE,
        ]

    @staticmethod
    def isMode(mode: str) -> bool:
        return Modes.getAllModes().__contains__(mode)

