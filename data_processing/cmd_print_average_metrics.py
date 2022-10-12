import argparse

from tabulate import tabulate

from command_functions import includeAutoscalers, includeMetrics, includeQueries, getAutoscalers, getMetrics, \
    getQueries, getDataFolder
from src.helperclasses import ExperimentFile, Experiment
from src.plotting import getAverageMetrics, getTotalRescalingActions



def printAverageData(source_folder: str, source_label: str, add_scaling_events: bool, queries: [str],
                     autoscalers: [str], metrics: [str]):
    """
    Print average data of all experiments found in a folder with a specific source_label
    :param source_folder: Source folder to search for experiments
    :param source_label: Prefix of the experiment files
    :param add_scaling_events: Also include total scaling events in metrics
    :param queries: List of queries that the experiments is allowed to have evaluated
    :param autoscalers: List of autoscalers that the experiments are allowed to have used
    :param metrics: List of metrics to print their average value from
    :return: None
    """
    data_folder = getDataFolder(source_folder)

    experiments: [Experiment] = Experiment.getAllExperiments(queries, autoscalers, label=source_label)
    experimentFiles: [ExperimentFile] = ExperimentFile.getAvailableExperimentFiles(data_folder, experiments,
                                                                                   printingEnabled=True)
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



def parseArguments():
    parser = argparse.ArgumentParser(description='Print averaged metrics')
    parser.add_argument('source_directory', type=str,
                        help="Directory in which datafiles can be found at src_dir/full-data")
    parser.add_argument('source_label', default="", type=str, nargs="?")
    parser.add_argument('--addscalingevents', action='store_true')
    includeAutoscalers(parser)
    includeMetrics(parser)
    includeQueries(parser)

    args = parser.parse_args()
    src_directory = args.source_directory
    src_label = args.source_label
    add_scaling_events = args.addscalingevents
    autoscalers = getAutoscalers(args)
    metrics = getMetrics(args)
    queries = getQueries(args)

    printAverageData(src_directory, src_label, add_scaling_events, queries, autoscalers, metrics)


if __name__ == "__main__":
    parseArguments()
