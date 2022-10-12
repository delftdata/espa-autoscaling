import argparse

from command_functions import includeAutoscalers, getAutoscalers, getDataFolder, getGraphFolder
from src.helperclasses import Metrics, ExperimentFile, Experiment, Queries
from src.plotting import pareto_plot


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


def parseArguments():
    validArguments = True

    parser = argparse.ArgumentParser(description='Print averaged metrics')
    parser.add_argument('src_dir', type=str)
    parser.add_argument('src_label', type=str)
    parser.add_argument('query', type=str)
    parser.add_argument('-xMetric', default="taskmanager", type=str, nargs="?")
    parser.add_argument('-xMetricLimit', type=float, nargs="?")
    parser.add_argument('-yMetric', default="latency", type=str, nargs="?")
    parser.add_argument('-yMetricLimit', type=float, nargs="?")
    includeAutoscalers(parser)

    args = parser.parse_args()
    autoscalers = getAutoscalers(args)
    src_dir = args.src_dir
    src_label = args.src_label
    query = args.query
    if not Queries.isQuery(query):
        print(f"Error: query {query} is not a valid query.")
        print(f"Possible queries: {Queries.getAllQueries()}")
        validArguments = False

    xMetric = args.xMetric
    if not Metrics.isMetricClass(xMetric):
        print(f"Error: xMetric {xMetric} is not a valid metric.")
        print(f"Possible metrics: {Metrics.getAllMetricClasses()}")
        validArguments = False

    yMetric = args.yMetric
    if not Metrics.isMetricClass(yMetric):
        print(f"Error: yMetric {yMetric} is not a valid metric.")
        print(f"Possible metrics: {Metrics.getAllMetricClasses()}")
        validArguments = False

    xMetricLimit = args.xMetricLimit
    yMetricLimit = args.yMetricLimit
    if validArguments:
        plotParetoPlot(src_dir, src_label, query, xMetric, yMetric, xMetricLimit, yMetricLimit, autoscalers)
    else:
        print("Canceled execution due to provided invalid arguments")


if __name__ == "__main__":
    parseArguments()