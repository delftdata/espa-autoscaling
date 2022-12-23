import argparse

from tabulate import tabulate
from Plotting import getAverageMetrics, getTotalRescalingActions
from ParameterProcessing import SingleFolderPlotParameters


def printAverageData(parameters: SingleFolderPlotParameters, add_scaling_events):
    experimentFiles = parameters.getExperimentFiles()
    header_row = ["Experiment"] + parameters.getMetrics()
    if add_scaling_events:
        header_row.append("Scaling_events")

    table = [header_row]
    for experimentFile in experimentFiles:
        results = getAverageMetrics(experimentFile, parameters.getMetrics())
        # Round results to 3 decimal if smaller than 1, else to 1
        results = list(map(lambda v: round(v, 3) if v < 1 else round(v, 1), results))
        if add_scaling_events:
            scalingEvents = getTotalRescalingActions(experimentFile)
            results.append(scalingEvents)
        row = [experimentFile.getExperimentName()] + results
        table.append(row)
    print(tabulate(table))


def parseArguments():
    # Create SingleFolderPlotParameters without a result folder and thresholds_option
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters(
        default_result_folder_name="",
        option_plot_thresholds=False,
        option_metric_ranges=False,
    )

    # Parse arguments
    parser = argparse.ArgumentParser(description='Print averaged metrics')
    parameters.includeArgumentsInParser(parser)
    parser.add_argument('--addscalingevents', action='store_true')

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetchArgumentsFromNamespace(namespace)
    add_scaling_events = namespace.addscalingevents

    # Call plot function
    printAverageData(
        parameters=parameters,
        add_scaling_events=add_scaling_events
    )


if __name__ == "__main__":
    parseArguments()
