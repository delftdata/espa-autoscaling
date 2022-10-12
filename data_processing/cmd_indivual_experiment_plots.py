import sys
import argparse

from command_functions import includeAutoscalers, includeMetrics, includeQueries, getAutoscalers, getMetrics, \
    getQueries, getDataFolder, getGraphFolder
from src.helperclasses import ExperimentFile, Experiment, Queries, Autoscalers, Metrics
from src.plotting import plotDataFile



def plotIndividualExperiments(folder, queries, autoscalers, metrics=None, label=""):
    """
    Create a plot of all available experiments from FOLDER of the characteristics of {queries}  and {autoscalers}.
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


def parseArguments():
    parser = argparse.ArgumentParser(description='Plot individual experiments')
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

    plotIndividualExperiments(src_directory, queries, autoscalers, metrics=metrics, label=src_label)


if __name__ == "__main__":
    parseArguments()
