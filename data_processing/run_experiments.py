from helperfunctions import fastCombineSimilarExperiments, deleteTooSmallLists
from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics
from plotting import plotDataFile, overlapAndPlotMultipleDataFiles, pareto_plot, getAverageMetrics, \
    getTotalRescalingActions
import sys
from tabulate import tabulate


def getDataFolder(folder):
    return f"{folder}/full-data"


def getGraphFolder(folder, create_graph_folder=True):
    if create_graph_folder:
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
                             queries, autoscalers, metrics=None):
    RESULT_FOLDER = f"{getGraphFolder(result_folder, create_graph_folder=False)}/"
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


def printAverageData(source_folder, source_label, add_scaling_events, autoscalers, queries, metrics):
    data_folder = getDataFolder(source_folder)

    experiments: [Experiment] = Experiment.getAllExperiments(queries, autoscalers, label=source_label)
    experimentFiles: [ExperimentFile] = ExperimentFile.getAvailableExperimentFiles(data_folder, experiments,
                                                                                   printingEnabled=False)

    table = []
    header_row = ["Experiment"] + metrics
    if add_scaling_events:
        header_row.append("Scaling_events")

    table.append(header_row)
    for experimentFile in experimentFiles:
        results = getAverageMetrics(experimentFile, metrics)
        results = list(map(lambda v: round(v, 3) if v < 1 else round(v, 1), results))
        if add_scaling_events:
            scalingEvents = getTotalRescalingActions(experimentFile)
            results.append(scalingEvents)
        row = [experimentFile.getExperimentName()] + results
        table.append(row)
    print(tabulate(table))



def plotParetoPlot(source_folder, source_label, src_query, xMetric, yMetric, xMetric_Limit, yMetric_Limit, autoscalers):
    data_folder = getDataFolder(source_folder)
    result_folder = f"{getGraphFolder(source_folder)}/pareto-plots"

    labelName = f"{source_label}_" if source_label != "" else ""
    xMetricName = f"{xMetric}[{xMetric_Limit}]" if xMetric_Limit else f"{xMetric}"
    yMetricName = f"{yMetric}[{yMetric_Limit}]" if yMetric_Limit else f"{yMetric}"

    fileName = f"{labelName}q{src_query}_{xMetricName}_{yMetricName}"

    experiments: [Experiment] = Experiment.getAllExperiments([src_query], autoscalers, label=source_label)
    experimentFiles: [ExperimentFile] = ExperimentFile.getAvailableExperimentFiles(data_folder, experiments)

    pareto_plot(experimentFiles, xMetric=xMetric, xMetricLimit=xMetric_Limit, yMetric=yMetric,
                yMetricLimit=yMetric_Limit, saveDirectory=result_folder, saveName=fileName)

# Todo: plot different experiment runs in a pareto plot
# def plotParetoPlotComparison(result_folder, result_file_name, folders_and_labels : [(str, str)], queries, autoscalers,
#                    xMetric=Metrics.TASKMANAGER, yMetric=Metrics.LATENCY):
#     result_folder = f"{getGraphFolder(result_folder, create_graph_folder=False)}/"
#
#     allExperimentFiles: [ExperimentFile] = []
#     for (folder, label) in folders_and_labels:
#         experiments: [Experiment] = Experiment.getAllExperiments(queries, autoscalers, label=label)
#
#         data_folder = getDataFolder(folder)
#         experimentFiles: [ExperimentFile] = ExperimentFile.getAvailableExperimentFiles(data_folder, experiments)
#
#         allExperimentFiles += experimentFiles
#
#     pareto_plot(allExperimentFiles, xMetric, yMetric, result_folder, result_file_name)



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
        # Metrics.INPUT_RATE,
        Metrics.TASKMANAGER,
        Metrics.LATENCY,
        # Metrics.LAG,
        # Metrics.THROUGHPUT,
        # Metrics.CPU_LOAD,
        # Metrics.BACKPRESSURE,
        # Metrics.BUSY_TIME,
        # Metrics.IDLE_TIME,
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
                                     queries, autoscalers, metrics)
        else:
            print(f"Error: Experiment {experiment} requires the following arguments: "
                  f"dest_folder result_label min_combinations[INT] min_combinations src_folder1 label1 src_folder2 "
                  f"label2 [src_foldern labeln]")

    elif experiment == "pareto":
        if len(arguments) >= 3:
            src_folder = arguments[0]
            src_label = arguments[1]

            query = arguments[2]
            if not Queries.isQuery(query):
                default_query = Queries.QUERY_1
                print(f"Error: query {query} is not a valid query, trying query {default_query} instead.")
                query = default_query

            xMetric = Metrics.TASKMANAGER
            yMetric = Metrics.LATENCY
            if len(arguments) >= 4:
                xMetricArg = arguments[3]
                if Metrics.isMetricClass(xMetricArg):
                    xMetric = xMetricArg
                else:
                    print(f"Error: xMetric {xMetricArg} is not a valid Metric. Using {xMetric} instead.")
            if len(arguments) >= 5:
                yMetricArg = arguments[4]
                if Metrics.isMetricClass(yMetricArg):
                    yMetric = yMetricArg
                else:
                    print(f"Error: yMetric {yMetricArg} is not a valid Metric. Using {yMetric} instead.")

            xMetric_Limit = None
            if len(arguments) >= 6:
                xMetricLimit_arg = arguments[5]
                if str.isdigit(xMetricLimit_arg):
                    xMetric_Limit = int(xMetricLimit_arg)
                else:
                    print(f"Error: {xMetricLimit_arg} is not a digit")

            yMetric_Limit = None
            if len(arguments) >= 7:
                yMetricLimit_arg = arguments[6]
                if str.isdigit(yMetricLimit_arg):
                    yMetric_Limit = int(yMetricLimit_arg)
                else:
                    print(f"Error: {yMetricLimit_arg} is not a digit")

            plotParetoPlot(src_folder, src_label, query, xMetric, yMetric, xMetric_Limit, yMetric_Limit, autoscalers)

        else:
            print(f"Error: Experiment {experiment} requires the following arguments:"
                  f"src_folder src_label query result_label (xMetric) (ymetric) (XMetricLimit) (yMetricLimit)")

    elif experiment == "averages":
        if len(arguments) >= 2:
            src_folder = arguments[0]
            src_label = arguments[1]
            add_scaling_events = False
            if len(arguments) >= 3:
                add_scaling_events = True if arguments[2].lower() == "true" else False
            printAverageData(src_folder, src_label, add_scaling_events, autoscalers, queries, metrics)
        else:
            print(f"Error: Experiment {experiment} requires the following arguments:"
                  f"src_folder src_label (add_scaling_events[boolean])")

    # Todo
    # elif experiment == "pareto-comparison":
    #     if len(arguments) >= 6 and len(arguments) % 2 == 0:
    #         destination_folder = arguments[0]
    #         result_file_name = arguments[1]
    #
    #         xMetric_default = Metrics.TASKMANAGER
    #         xMetric = arguments[2]
    #         if not Metrics.isMetricClass(xMetric):
    #             print(f"Error: xMetric {xMetric} is not a valid Metric. Using {xMetric_default} instead.")
    #             xMetric =xMetric_default
    #
    #         yMetric = arguments[3]
    #         yMetric_default = Metrics.LATENCY
    #         if not Metrics.isMetricClass(yMetric):
    #             print(f"Error: yMetric {yMetric} is not a valid Metric. Using {yMetric_default} instead.")
    #             yMetric = yMetric_default
    #
    #         remaining_arguments = arguments[4:]
    #         folders_and_labels = list(zip(remaining_arguments[0::2], remaining_arguments[1::2]))
    #
    #         plotParetoPlot(destination_folder, result_file_name, folders_and_labels, queries, autoscalers,
    #                        xMetric, yMetric)
    #     else:
    #         print(f"Error: Experiment { experiment} requires the following arguments:"
    #               f"dest_folder result_name xMetric yMetric src_folder1 label1 src_folder2 "
    #               f"label2 [src_foldern labeln]")


    elif experiment in ["help", "-h", "h"]:
        print("The following experiments are supported:")
        print("|- individual src_folder (label)")
        print("|- autoscaler src_folder (label)")
        print("|- comparison dest_folder result_label src_folder1 label1 src_folder2 label2 [src_foldern labeln]")
        print("|- pareto src_folder src_prefix query (xMetric) (ymetric)")
        print("|- averages src_folder src_label")
    else:
        print(f"Experiment {experiment} was not recognized. Run -h to view the options.")


if __name__ == "__main__":
    plotRedoneExperiment()




