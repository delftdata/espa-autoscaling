from DataClasses import ExperimentFile

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


def deleteTooSmallLists(experimentFiles: [[ExperimentFile]], minimumSize: int):
    return list(filter(lambda l: len(l) >= minimumSize, experimentFiles))