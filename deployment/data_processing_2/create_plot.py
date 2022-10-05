import pandas as pd
import matplotlib.pyplot as plt
import helperclasses as hc
from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics

DATA_FOLDER = "./results/full_results"
RESULT_FOLDER = "./results/plots"


def plotExperiment(queryNumber="1", autoscaler="dhalion", setting="1", metrics=None, savePlot=False):
    # Plot all metrics if no subset was provided
    source_name = f"q{queryNumber}_{autoscaler}_{setting}.csv"
    inputFile = f"{DATA_FOLDER}/{source_name}"
    plotDataFile(inputFile, metrics, savePlot)


def plotDataFile(inputFile: str, metrics=None):
    if metrics is None:
        metrics = getAllMetricClasses()

    data = pd.read_csv(inputFile)
    time_column = data["minutes"]

    # fig, axs = plt.subplots(len(metrics))
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)

    for i in range(len(metrics)):

        # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
        metricName = metrics[i]
        metric_column = data[metricName]
        axis = axs[i] if len(metrics) > 1 else axs

        # Set axis
        axis.plot(time_column, metric_column, color="red")
        axis.title.set_text(metricName)
        axis.set_ylim([0, metric_column.max() * 1.2])
        axis.grid()

        # Set xlabel on final subplot
        if i == len(metrics) - 1:
            axis.set_xlabel("Minutes")

    plt.show()


def overlapAndPlotMultipleDataFiles(inputFile: [str], metrics=None):
    if metrics is None:
        metrics = getAllMetricClasses()

    datalist = list(map(lambda file: pd.read_csv(inputFile)))

    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)

    for i in range(len(metrics)):
        metricName = metrics[i]
        axis = axs[i] if len(metrics) > 1 else axs

        maxMetric = -1
        for data in datalist:
            time_column = data["minutes"]
            metric_column = data[metricName]
            axis.plot(time_column, metric_column)
            maxMetric = max(maxMetric, metric_column.max())
        axis.title.set_text(metricName)
        axis.set_ylim([0, maxMetric * 1.2])
        axis.grid()

        if i == len(metrics) - 1:
            axis.set_xlabel("Minutes")


if __name__ == "__main__":
    queries = [
        Queries.QUERY_1,
        # Queries.QUERY_3,
        # Queries.QUERY_11
    ]
    autoscaler = [
        Autoscalers.DHALION,
        Autoscalers.DS2_ORIGINAL,
        Autoscalers.DS2_UPDATED,
        # Autoscalers.HPA,
        Autoscalers.VARGA1,
        Autoscalers.VARGA2,
    ]
    experiments = Experiment.getAllExperiments(queries, autoscaler)
    experimentFiles = ExperimentFile.getAvailableExperimentFiles(DATA_FOLDER, experiments)

    allExperimentFiles = ExperimentFile.getAllAvailableExperimentFiles(DATA_FOLDER, printingEnabled=False)

    # print(hc.getAllExperiments())
    # m = [
    #     Metrics.IDLE_TIME,
    # ]
    # plotExperiment()
