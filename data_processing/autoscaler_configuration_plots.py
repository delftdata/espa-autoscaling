import argparse

from command_functions import getQueries, getMetrics, getAutoscalers, includeQueries, includeMetrics, \
    includeAutoscalers, getGraphFolder, getDataFolder
from src.helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics
from src.plotting import overlapAndPlotMultipleDataFiles


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



def parseArguments():
    parser = argparse.ArgumentParser(description='Plot autoscaler configuration comparisons')
    parser.add_argument('source_directory', type=str,
                        help="Directory in which datafiles can be found at src_dir/full-data")
    parser.add_argument('source_label', default="", type=str, nargs="?")
    includeAutoscalers(parser)
    includeMetrics(parser)
    includeQueries(parser)

    args = parser.parse_args()
    src_directory = args.source_directory
    src_label = args.source_label
    autoscalers = getAutoscalers(args)
    metrics = getMetrics(args)
    queries = getQueries(args)

    plotAutoscalerConfigurations(src_directory, queries, autoscalers, metrics=metrics, label=src_label)


if __name__ == "__main__":
    parseArguments()