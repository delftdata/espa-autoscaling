import pandas as pd
import matplotlib.pyplot as plt
import helperclasses as hc
from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics


DATA_FOLDER = "./results/full_results"
RESULT_FOLDER = "./results/plots"


def stylePlots():
    plt.style.use('seaborn-dark-palette')



def plotDataFile(file: ExperimentFile, metrics=None):
    """
    Create a plot of a datafile with the provided metrics
    :param file: Datafile to create a plot from
    :param metrics: Metrics to visualise in the plot. if left None, all available metrics will be used.
    :return: None
    """
    if metrics is None:
        metrics = Metrics.getAllMetricClasses()

    data = pd.read_csv(file.datafile)
    time_column = data["minutes"]

    # fig, axs = plt.subplots(len(metrics))
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    stylePlots()

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


def overlapAndPlotMultipleDataFiles(files: [ExperimentFile], metrics=None):
    """
    Combine the results of the provided metrics of multiple experiments in a single plot
    :param files: List of datafiles af datafiles to create a plot from
    :param metrics: Metrics to visualise in the plot. if left None, all available metrics will be used.
    :return: None
    """
    # If no metrics provided, use all metrics
    if metrics is None:
        metrics = Metrics.getAllMetricClasses()

    # Get list of (Experiment, pd dataframe)
    datalist = list(map(lambda file: (file.experiment, pd.read_csv(file.datafile)), files))

    # Create pyplot and style it
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    stylePlots()

    # For every metric
    for i in range(len(metrics)):
        metricName = metrics[i]
        axis = axs[i] if len(metrics) > 1 else axs

        # Calculate maximum value to set Y-axis
        maxMetric = -1

        # Plot every datafile in the graph
        for (experiment, data) in datalist:
            time_column = data["minutes"]
            metric_column = data[metricName]
            line, = axis.plot(time_column, metric_column)
            line.set_label(f"q{experiment.query}_{experiment.autoscaler}_{experiment.variable}")
            maxMetric = max(maxMetric, metric_column.max())
        # Style graph and set title of the graph
        axis.title.set_text(metricName)
        axis.set_ylim([0, maxMetric * 1.2])
        axis.grid()

        # Finalise plot style when handling the last metric
        if i == len(metrics) - 1:
            axis.set_xlabel("Minutes")
            # legend should be placed in in a different location when only using on metric
            if len(metrics) > 1:
                axis.legend(loc='lower right', bbox_to_anchor=(1.11, -0.2))
            else:
                axis.legend(loc='lower right', bbox_to_anchor=(1.12, 0))
    plt.show()


if __name__ == "__main__":
    queries = [
        Queries.QUERY_1,
        # Queries.QUERY_3,
        # Queries.QUERY_11
    ]
    autoscaler = [
        Autoscalers.DHALION,
        # Autoscalers.DS2_ORIGINAL,
        # Autoscalers.DS2_UPDATED,
        # Autoscalers.HPA,
        # Autoscalers.VARGA1,
        # Autoscalers.VARGA2,
    ]
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

    experiments = Experiment.getAllExperiments(queries, autoscaler)
    experimentFiles = ExperimentFile.getAvailableExperimentFiles(DATA_FOLDER, experiments)

    overlapAndPlotMultipleDataFiles(ExperimentFile.getAllAvailableExperimentFiles(DATA_FOLDER), metrics=metrics)

