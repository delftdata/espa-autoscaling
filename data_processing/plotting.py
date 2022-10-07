import pandas as pd
import matplotlib.pyplot as plt
from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics


def stylePlots():
    plt.style.use('seaborn-dark-palette')


def plotDataFile(file: ExperimentFile, metrics=None):
    """
    Create a plot of a datafile with the provided metrics
    :param file: Datafile to create a plot from
    :param metrics: Metrics to visualise in the plot. if left None, all available metrics will be used.
    :return: None
    """
    if not file:
        print(f"Error: no datafile found.")

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
    if not files:
        print(f"Error: no datafiles found.")

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

            experimentLabel = experiment.getExperimentName()
            line.set_label(experimentLabel)

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

