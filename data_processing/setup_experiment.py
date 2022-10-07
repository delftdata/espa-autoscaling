from helperclasses import *
from plotting import overlapAndPlotMultipleDataFiles

# REDUNDANT, APPEARS TO BE MUCH EASIER USING A FOR SINGLE FOR LOOP
def combineAllSimilarExperiments(experiments: [[ExperimentFile]], ignoreLabel=True):
    """
    Given a list of experiment executions, who performed similar experiments that have to be compared.
    This function binds together all experiments that were performed by all experiment executions and are similar
    to each other.
    The final result is a list containing lists of ExperimentFiles that were
        1. Present in all experiment runs found in experiments
        2. Are all similar to each others

    :param experiments: A list of executions, all containing a set of ExperimentFiles. Experiments is structured in
    the following way:
        [ [experimentFiles of execution 2], [experimentFiles of execution 1], [experimentFiles of execution 2]
    :param ignoreLabel: Whether to ignore the label of the experiments when comparing them
    :return: A list of results containing a list of Experiment Files. This is structured the following way:
        [ [experimentFile of execution 0, experimentFile of execution 1, experimentFile of execution 2],
          [experimentFile of execution 0, experimentFile of execution 1, experimentFile of execution 2],
          [experimentFile of execution 0, experimentFile of execution 1, experimentFile of execution 2] ]
    """
    return __combineSimilarExperiments([], experiments, 0, ignoreLabel)

# REDUNDANT, APPEARS TO BE MUCH EASIER USING A FOR SINGLE FOR LOOP
def __combineSimilarExperiments(result: [[ExperimentFile]], itr: [[ExperimentFile]], columnsProcessed, ignoreLabel):
    """
    Recursive algorithm to get a list of all similar experiments found in the different lists of itr.
    The algorithm will return a list containing lists of similar results all found in itr.

    :param result: The result we found until now
    :param itr: A list of lists containing experiments. The structure is as follows:
    [   [ experiments_run_1 ] , [ experiments_run_2 ] , [ experiments_run_3]    ]
    :param itemsProcessed: Amount of columns
    :param ignoreLabel: Whether to ignore the labels in comparing experiments
    :return: A list of lists containing a single item from every row of itr that is similar to all other items.
    """

    if not itr:
        # If nothing left to do: return result
        return result
    if columnsProcessed == 0:
        # First step of recursion
        # 1. Copy make a list of every item of the first column of to itr and copy it to result
        # 2. Call recursive loop with new done and remove column from itr
        done = list(map(lambda l: [l], itr[0]))
        return __combineSimilarExperiments(done, itr[1:], 1, ignoreLabel)
    else:
        # Merge result and itr by
        # 1. Adding similar experiments of the itr column to result
        # 2. Removing results who did not find a similar experiment in itr
        # 3. Remove column from itr and call next recursive loop
        for exp in itr[0]:
            for resultList in result:
                if resultList[0].experiment.isSimilarExperiment(exp.experiment, ignoreLabel):
                    resultList.append(exp)
        done = list(filter(lambda l: len(l) == columnsProcessed + 1, result))
        return __combineSimilarExperiments(done, itr[1:], columnsProcessed + 1, ignoreLabel)




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

###############################
## Plotting

def plotSetupExperiment():
    DATA_FOLDER_SETUP = "./results/setup"

    # Get all experiments of run n1
    experimentFiles_n1 = ExperimentFile.getAllAvailableExperimentFiles(DATA_FOLDER_SETUP, label="1n", printingEnabled=False)

    # Get all experiments of run n2
    experimentFiles_n4 = ExperimentFile.getAllAvailableExperimentFiles(DATA_FOLDER_SETUP, label="4n", printingEnabled=False)

    # Get all experiments of run original (performed by Wiebe)
    experimentFiles_original = ExperimentFile.getAllAvailableExperimentFiles(DATA_FOLDER_SETUP, label="original", printingEnabled=False)


    allExperiments = experimentFiles_original + experimentFiles_n4 # experimentFiles_n1
    mergedExperiments = fastCombineSimilarExperiments(allExperiments)
    mergedExperiments = deleteTooSmallLists(mergedExperiments, 2)
    for experimentFileList in mergedExperiments:
        overlapAndPlotMultipleDataFiles(experimentFileList)



if __name__ == "__main__":
    plotSetupExperiment()