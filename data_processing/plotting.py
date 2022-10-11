import matplotlib.pyplot
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
from matplotlib.transforms import Bbox

from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics
import os.path

def stylePlots():
    plt.style.use('seaborn-dark-palette')



def savePlot(plt, saveDirectory, saveName, bbox_inches=None, dpi=None):
    if not os.path.exists(saveDirectory):
        print(f"Creating save-directory {saveDirectory}")
        os.makedirs(saveDirectory)
    fileLocation = f"{saveDirectory}/{saveName}.png"
    plt.savefig(fileLocation, bbox_inches=bbox_inches, dpi=dpi)
    print(f"Saved graph at: {fileLocation}")


def plotDataFile(file: ExperimentFile, saveDirectory=None, metrics=None):
    """
    Create a plot of a datafile with the provided metrics
    :param saveDirectory: directory to save the plot in. If left None, the plot is only shown.
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

    stylePlots()
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)

    for i in range(len(metrics)):

        # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
        metricName = metrics[i]
        metric_column = data[metricName]
        axis = axs[i] if len(metrics) > 1 else axs

        # Set axis
        axis.plot(time_column, metric_column)
        axis.title.set_text(metricName)
        axis.set_ylim([0, metric_column.max() * 1.2])
        axis.grid()

        # Set xlabel on final subplot
        if i == len(metrics) - 1:
            axis.set_xlabel("Minutes")

    if saveDirectory:
        savePlot(plt, saveDirectory, file.experiment.getExperimentName())
        plt.close()
    else:
        plt.show()


def overlapAndPlotMultipleDataFiles(files: [ExperimentFile], metrics=None, saveDirectory=None, saveName=None):
    """
    Combine the results of the provided metrics of multiple experiments in a single plot
    :param saveName: Name of the plot. This should only be the name and no extensions. if left None, the plot is only shown.
    :param saveDirectory: Directory to save the plot in. If left None, the plot is only shown.
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

    stylePlots()
    # Create pyplot and style it
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)

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

    if saveDirectory and saveName:
        savePlot(plt, saveDirectory, saveName)
        plt.close()
    else:
        plt.show()

def getAverageMetricFromData(data, metricName):
    metric_column = data[metricName]
    return sum(metric_column) / len(metric_column)


def getAverageMetric(experimentFile: ExperimentFile, metricName: str):
    data = pd.read_csv(experimentFile.datafile)
    return getAverageMetricFromData(data, metricName)


def getAverageMetrics(experimentFile: ExperimentFile, metrics):
    data = pd.read_csv(experimentFile.datafile)
    results = []
    for metric in metrics:
        results.append(getAverageMetricFromData(data, metric))
    return results


def getTotalRescalingActions(experimentFile: ExperimentFile):
    data = pd.read_csv(experimentFile.datafile)
    taskmanagers = data['taskmanager'].tolist()
    previous_number_taskmanagers = taskmanagers[0]
    scaling_events = 0
    for val in taskmanagers:
        if val != previous_number_taskmanagers:
            scaling_events += 1
        previous_number_taskmanagers = val
    return scaling_events



def pareto_plot(experimentFiles: [ExperimentFile], xMetric=Metrics.TASKMANAGER, xMetricLimit=None,
                yMetric=Metrics.LATENCY, yMetricLimit=None, saveDirectory=None, saveName=None):
    autoscaler_layout = {
        Autoscalers.HPA: ("red", "o"), # (color, marker)
        Autoscalers.VARGA1: ("purple", "*"),
        Autoscalers.VARGA2: ("orange", "P"),
        Autoscalers.DHALION: ("green", "X"),
        Autoscalers.DS2_ORIGINAL: ("pink", "D"),
        Autoscalers.DS2_UPDATED: ("brown", "s"),
    }

    xMetric_values = []
    yMetric_values = []
    seen_autoscalers = []
    texts = []
    fig, ax = plt.subplots()
    for experimentFile in experimentFiles:
        xMetric_avg = getAverageMetric(experimentFile, xMetric)
        xMetric_values.append(xMetric_avg)

        yMetric_avg = getAverageMetric(experimentFile, yMetric)
        yMetric_values.append(yMetric_avg)

        if xMetricLimit and xMetric_avg > xMetricLimit:
           continue
        if yMetricLimit and yMetric_avg > yMetricLimit:
           continue

        autoscaler = experimentFile.getAutoscaler()
        color, marker = autoscaler_layout[experimentFile.getAutoscaler()]

        legend_label = f"{autoscaler}" if autoscaler not in seen_autoscalers else ""
        ax.scatter(xMetric_avg, yMetric_avg, s=50, color=color, marker=marker, label=legend_label)
        seen_autoscalers.append(autoscaler)
        texts.append(ax.text(xMetric_avg, yMetric_avg, experimentFile.getVariable(), ha='right', va='top', size=10))

    if xMetricLimit:
        plt.xlim((0, xMetricLimit))
    if yMetricLimit:
        plt.ylim((0, yMetricLimit))

    # if zoomed:
    #     plt.ylim([0,zoomed_latency_limit])
    #     plt.xlim([0,16])
    # else:
    #     plt.ylim([0,latency_limit])
    #     plt.xlim([0,16])

    plt.legend(loc=(1.02,0.5), labelspacing=1)
    plt.grid()
    # todo: create better axis titles
    plt.xlabel(f"Average {xMetric}")
    plt.ylabel(f"Average {yMetric}")

    adjust_text(texts, only_move={'points':'y', 'texts':'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0))

    if saveDirectory and saveName:
        savePlot(plt, saveDirectory, saveName, bbox_inches=Bbox([[0, 0], [8.0, 5.0]]), dpi=600)
        plt.close()
    else:
        plt.show()

