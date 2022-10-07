from helperfunctions import fastCombineSimilarExperiments, deleteTooSmallLists
from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics
from plotting import plotDataFile, overlapAndPlotMultipleDataFiles
import sys


def getDataFolder(folder):
    return f"{folder}/full-data"


def getGraphFolder(folder, graph_folder=True):
    if graph_folder:
        return f"{folder}/graphs"
    else:
        return f"{folder}"


def plotIndividualExperiments(folder, queries, autoscalers, metrics=None, label=""):
    """
    Createa  plot of all available experiments from FOLDER of the characteristics of {queries}  and {autoscalers}.
    Individual plots are created of metrics {metrics}
    :param queries: Queries to create a plot from
    :param autoscalers: Autoscalers to create a plot from
    :param folder: Folder to fetch the data and save the plots
    :param metrics: Metrics to create plots from
    :param label: Optional prefix of experiments to differentiate between different experiments
    :return: None
    """
    DATA_FOLDER = getDataFolder(folder)
    RESULT_FOLDER = f"{getGraphFolder(folder)}/individual-plots"

    experiments = Experiment.getAllExperiments(queries, autoscalers, label=label)
    experimentFiles = ExperimentFile.getAvailableExperimentFiles(DATA_FOLDER, experiments)

    for experimentFile in experimentFiles:
        plotDataFile(experimentFile, saveDirectory=RESULT_FOLDER, metrics=metrics)


def plotAutoscalerConfigurations(folder, queries, autoscalers, metrics=None, label=""):
    """
    Create combined plots per query of every autoscaler configuration.
    For every query and every autoscaler, a plot is created containing all runs of the autoscaler with different configurations.
    :param queries: Queries to create a plot from
    :param autoscalers: Autoscalers to create a plot form
    :param folder: Folder to fetch the data and save plots
    :param metrics: Metrics to create plots from
    :param label: Optional prefix of experiments to differentiate between different experiments
    :return: None
    """
    DATA_FOLDER = getDataFolder(folder)
    RESULT_FOLDER = f"{getGraphFolder(folder)}/autoscaler-variables-combined"

    for query in queries:
        for autoscaler in autoscalers:
            experiments = Experiment.getAllExperiments(query, autoscaler, label=label)
            experimentFiles = ExperimentFile.getAvailableExperimentFiles(DATA_FOLDER, experiments)
            if len(experimentFiles) > 0:
                labelName = f"{label}_" if label != "" else ""
                fileName = f"{labelName}q{query}_{autoscaler}"
                overlapAndPlotMultipleDataFiles(experimentFiles, saveDirectory=RESULT_FOLDER, saveName=fileName, metrics=metrics)


def plotExperimentComparison(result_folder, result_label, minimumCombinations, folders_and_labels : [(str, str)],
                             queries, autoscalers, metrics=None, graph_folder=True):
    RESULT_FOLDER = f"{getGraphFolder(result_folder, graph_folder)}/experiment-comparisons"
    allExperimentFiles: [ExperimentFile] = []
    for (folder, label) in folders_and_labels:
        folder = getDataFolder(folder)
        # Fetch all possible experiments that can be created using {queries}  and {autoscalers}
        experiments: [Experiment] = Experiment.getAllExperiments(queries, autoscalers, label=label)
        # Fetch all files that correspond to these experiments in folder {folder}
        experimentFiles: [ExperimentFile] = ExperimentFile.getAvailableExperimentFiles(folder, experiments)
        # Append the found files to the allExperimentFiles list
        allExperimentFiles += experimentFiles

    # Combine all ExperimentFiles that ran on the same query, with the same autoscaler and the same configuration.
    # Labels are allowed to differ (as ignoreLabel = True)
    experimentFileLists: [[ExperimentFile]] = fastCombineSimilarExperiments(allExperimentFiles, ignoreLabel=True)
    # Remove all combinations that hold less than {minimumCombinations} amount of files
    experimentFileLists: [[ExperimentFile]] = deleteTooSmallLists(experimentFileLists, minimumCombinations)

    # For every found combination, we create a plot
    for experimentFileList in experimentFileLists:
        expFile0: ExperimentFile = experimentFileList[0]
        query = expFile0.getQuery()
        autoscaler = expFile0.getAutoscaler()
        variable = expFile0.getVariable()

        labelName = f"{result_label}_" if result_label != "" else ""
        fileName = f"{labelName}q{query}_{autoscaler}_{variable}"
        overlapAndPlotMultipleDataFiles(experimentFileList, saveDirectory=RESULT_FOLDER, saveName=fileName,
                                        metrics=metrics)


def plotRedoneExperiment():
    ###########################################################
    # Configurations:

    # List of queries to consider when searching for expeirments to plot
    queries = [
        Queries.QUERY_1,
        Queries.QUERY_3,
        Queries.QUERY_11
    ]
    # List of autoscalers to consider when searching for experiments to plot
    autoscalers = [
        Autoscalers.DHALION,
        Autoscalers.DS2_ORIGINAL,
        Autoscalers.DS2_UPDATED,
        Autoscalers.HPA,
        Autoscalers.VARGA1,
        Autoscalers.VARGA2,
    ]
    # List of metrics to display in plots
    metrics = [
        Metrics.INPUT_RATE,
        Metrics.TASKMANAGER,
        Metrics.LATENCY,
        Metrics.LAG,
        Metrics.THROUGHPUT,
        Metrics.CPU_LOAD,
        Metrics.BACKPRESSURE,
        Metrics.BUSY_TIME,
        Metrics.IDLE_TIME,
    ]

    experiment = sys.argv[1]
    arguments = sys.argv[2:]
    if experiment == "individual":
        # Create a combined plot of every autoscaler including its runs with specific configurations
        # Arg1: folder to fetch information from
        # Arg2 (optional): label to place
        if len(arguments) in range(1, 3):
            folder = arguments[0]
            label = arguments[1] if len(arguments) > 1 else ""
            plotIndividualExperiments(folder, queries, autoscalers, label=label)
        else:
            print(f"Error: Experiment {experiment} requires the following arguments: folder (label).")

    elif experiment == "autoscaler":
        # Create a combined plot of every autoscaler including its runs with specific configurations
        # Arg1: folder to fetch information from
        # Arg2 (optional: label to place
        if len(arguments) in range(1, 3):
            folder = arguments[0]
            label = arguments[1] if len(arguments) > 1 else ""
            plotAutoscalerConfigurations(folder, queries, autoscalers, label=label)
        else:
            print(f"Error: Experiment {experiment} requires the following arguments: folder (label).")


    elif experiment == "comparison":
        if len(arguments) >= 7 and len(arguments) % 2 == 1 and str.isdigit(arguments[2]):
            destination_folder = arguments[0]
            result_label = arguments[1]
            min_combinations = int(arguments[2])
            remaining_arguments = arguments[3:]
            comparison_folders_and_labels = list(zip(remaining_arguments[0::2], remaining_arguments[1::2]))
            plotExperimentComparison(destination_folder, result_label, min_combinations, comparison_folders_and_labels,
                                     queries, autoscalers, metrics, graph_folder=False)
        else:
            print(f"Error: Experiment {experiment} requires the following arguments: "
                  f"dest_folder result_label min_combinations[INT] min_combinations src_folder1 label1 src_folder2 "
                  f"label2 [src_foldern labeln]")

    elif experiment in ["help", "-h", "h"]:
        print("The following experiments are supported:")
        print("|- individual src_folder (label)")
        print("|- autoscaler src_folder (label)")
        print("|- comparison dest_folder result_label src_folder1 label1 src_folder2 label2 [src_foldern labeln]")
    else:
        print(f"Experiment {experiment} was not recognized. Run -h to view the options.")


if __name__ == "__main__":
    plotRedoneExperiment()




