import argparse

from tabulate import tabulate

from command_functions import includeAutoscalers, includeMetrics, includeQueries, getAutoscalers, getMetrics, \
    getQueries, getDataFolder
from src.helperclasses import ExperimentFile, Experiment
from src.plotting import getAverageMetrics, getTotalRescalingActions



def printAverageData(source_folder, source_label, add_scaling_events, queries, autoscalers, metrics):
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
    parser.add_argument('--scalingevents', action='store_true')
    includeAutoscalers(parser)
    includeMetrics(parser)
    includeQueries(parser)

    args = parser.parse_args()
    src_directory = args.source_directory
    src_label = args.source_label
    add_scaling_events = args.scalingevents
    autoscalers = getAutoscalers(args)
    metrics = getMetrics(args)
    queries = getQueries(args)

    printAverageData(src_directory, src_label, add_scaling_events, queries, autoscalers, metrics)


if __name__ == "__main__":
    parseArguments()
