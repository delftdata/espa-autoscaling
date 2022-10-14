from DataClasses import ExperimentFile


class StaticPlotFunctions:
    # Shared folder structures
    @staticmethod
    def getDefaultDataFolder(main_folder: str):
        return f"{main_folder}/full-data"

    @staticmethod
    def getDefaultGraphFolder(main_folder: str, include_graph_folder=True):
        if include_graph_folder:
            return f"{main_folder}/graphs"
        else:
            return f"{main_folder}"

    # Naming functionality
    @staticmethod
    def getNamingPrefix(prefix: str):
        return "" if prefix == "" else f"{prefix}_"

    @staticmethod
    def getNamingPostfix(postfix: str):
        return "" if postfix == "" else f"_{postfix}"

    @staticmethod
    def fastCombineSimilarExperiments(experimentFiles: [ExperimentFile], ignoreLabel=True):
        """
        Function combines all similar experiments in a single list.
        :param experimentFiles: ExperimentFiles to combine all similar experiments
        :param ignoreLabel: Whether to ignor ethe label recognizing simmilar experiments
        :return: List of lists containing all similar experiments
        """
        combinations = []
        for experimentFile in experimentFiles:
            found = False
            for combination in combinations:
                if experimentFile.experiment.isSimilarExperiment(combination[0].experiment, ignoreLabel=ignoreLabel):
                    combination.append(experimentFile)
                    found = True
                    break
            if not found:
                combinations.append([experimentFile])
        return combinations

    @staticmethod
    def deleteTooSmallLists(experimentFiles: [[ExperimentFile]], minimumSize: int):
        return list(filter(lambda l: len(l) >= minimumSize, experimentFiles))