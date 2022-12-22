# from typing import Tuple

# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib.transforms import Bbox
from DataClasses import ExperimentFile, Autoscalers, Metrics, Experiment
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


def getMetricColumn(metric, data):
    if metric in data:
        return data[metric]
    else:
        print(f"Warning: metric {metric} not found")
        return None

#
# def addThresholdLine(ax, experiment: Experiment, metric: str, time_column, dataFrame):
#     if experiment.autoscaler == Autoscalers.DHALION:
#         # Overprovisioning
#         color = "green"
#         if metric == Metrics.CPU_LOAD:
#             # CPU_Load < 0.6
#             ax.axhline(0.6, color=color, linewidth=2.5)
#         elif metric == Metrics.BACKPRESSURE:
#             # Backpressure < 100
#             ax.axhline(100, color=color, linewidth=2.5)
#         elif metric == Metrics.LAG:
#             throughput_dataframe = dataFrame[Metrics.INPUT_RATE]
#             taskmanager_dataframe = dataFrame[Metrics.TASKMANAGER]
#             threshold_data = 0.2 * taskmanager_dataframe * throughput_dataframe
#             ax.plot(time_column, threshold_data, color=color)
#
#         # Underprovisioning
#         color = "red"
#         if metric == Metrics.LATENCY:
#             # Average event time lag < flink_taskmanager_job_task_operator_currentEmitEventTimeLag
#             # latench = variable
#             val = experiment.variable
#             ax.axhline(float(val), color=color, linewidth=2.5)
#
#     if experiment.autoscaler == Autoscalers.HPA:
#         color = "red"
#         if metric == Metrics.CPU_LOAD:
#             val = float(f"0.{experiment.variable}")
#             ax.axhline(val, color=color, linestyle='dotted', linewidth=2.5)
#
#     if experiment.autoscaler in [Autoscalers.VARGA1, Autoscalers.VARGA2]:
#         color = "red"
#         if metric == Metrics.IDLE_TIME:
#             value = 1 - float(experiment.variable)
#             ax.axhline(value, color=color, linestyle='dotted', linewidth=2.5)
#         if metric == Metrics.LAG:
#             ax.axhline(50000, color=color, linewidth=2.5)
#         if metric == Metrics.VARGA_RELATIVE_LAG_CHANGE_RATE:
#             ax.axhline(1.0, color=color, linestyle='dotted', linewidth=2.5)
#
#     if experiment.autoscaler == Autoscalers.DS2_UPDATED:
#         # Underprovisioning
#         color = "red"
#         if metric == Metrics.LATENCY:
#             ax.axhline(5, color=color, linewidth=1.5)
#
#         # Overprovisioning
#         color = "green"
#         if metric == Metrics.LATENCY:
#             ax.axhline(1, color=color, linewidth=1.5)

#
# def getYrange(metricName: str, min_val, max_val, metric_ranges) -> Tuple[float, float]:
#     # If specific range is specified
#     for metric_range in metric_ranges:
#         if metric_range[0] == metricName:
#             return metric_range[1], metric_range[2]
#
#     # Else we fetch the default ranges
#     min_range, max_range = Metrics.getDefaultRange(metricName)
#     if min_range is None:
#         min_range = min_val
#     if max_range is None:
#         max_range = max_val
#     return min_range, max_range







# def overlapAndPlotMultipleDataFiles(
#         files: [ExperimentFile],
#         metrics=None,
#         metric_ranges: Tuple[str, float, float] = None,
#         saveDirectory=None,
#         saveName=None,
# ):
#     """
#     Combine the results of the provided metrics of multiple experiments in a single plot
#     :param saveName: Name of the plot. This should only be the name and no extensions. if left None, the plot is only shown.
#     :param saveDirectory: Directory to save the plot in. If left None, the plot is only shown.
#     :param files: List of datafiles af datafiles to create a plot from
#     :param metric_ranges
#     :param metrics: Metrics to visualise in the plot. if left None, all available metrics will be used.
#     :return: None
#     """
#     if metric_ranges is None:
#         metric_ranges = []
#     if not files:
#         print(f"Error: no datafiles found.")
#
#     # If no metrics provided, use all metrics
#     if metrics is None:
#         metrics = Metrics.get_all_metric_classes()
#
#     # Get list of (Experiment, pd dataframe)
#     datalist = list(map(lambda file: (file.experiment, pd.read_csv(file.datafile)), files))
#
#     stylePlots()
#     # Create pyplot and style it
#     fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
#     fig.subplots_adjust(hspace=.5, wspace=.001)
#
#     # For every metric
#     for i in range(len(metrics)):
#         metricName = metrics[i]
#         axis = axs[i] if len(metrics) > 1 else axs
#
#         # Calculate maximum value to set Y-axis
#         maxMetric = float('-inf')
#         minMetric = float('inf')
#
#         # Plot every datafile in the graph
#         for (experiment, data) in datalist:
#             time_column = data["minutes"]
#             metric_column = getMetricColumn(metricName, data)
#             line, = axis.plot(time_column, metric_column)
#
#             experimentLabel = experiment.getExperimentName()
#             line.set_label(experimentLabel)
#
#             maxMetric = max(maxMetric, metric_column.max())
#             minMetric = min(minMetric, metric_column.min())
#             if plotThresholds:
#                 addThresholdLine(axis, experiment, metricName, time_column, data)
#
#         # Style graph and set title of the graph
#         axis.title.set_text(metricName)
#
#         yLim_min, yLim_max = getYrange(metricName, minMetric, maxMetric, metric_ranges)
#         axis.set_ylim([yLim_min, yLim_max])
#         axis.grid()
#
#         # Finalise plot style when handling the last metric
#         if i == len(metrics) - 1:
#             axis.set_xlabel("Minutes")
#             # legend should be placed in in a different location when only using on metric
#             if len(metrics) > 1:
#                 axis.legend(loc='lower right', bbox_to_anchor=(1.11, -0.2))
#             else:
#                 axis.legend(loc='lower right', bbox_to_anchor=(1.12, 0))
#
#     if saveDirectory and saveName:
#         savePlot(plt, saveDirectory, saveName)
#         plt.close()
#     else:
#         plt.show()


# def getAverageMetricFromData(data, metricName):
#     metric_column = data[metricName]
#     return sum(metric_column) / len(metric_column)
#
#
# def getAverageMetric(experimentFile: ExperimentFile, metricName: str):
#     data = pd.read_csv(experimentFile.datafile)
#     return getAverageMetricFromData(data, metricName)
#
#
# def getAverageMetrics(experimentFile: ExperimentFile, metrics):
#     data = pd.read_csv(experimentFile.datafile)
#     results = []
#     for metric in metrics:
#         results.append(getAverageMetricFromData(data, metric))
#     return results
#
#
# def getTotalRescalingActions(experimentFile: ExperimentFile):
#     data = pd.read_csv(experimentFile.datafile)
#     taskmanagers = data['taskmanager'].tolist()
#     previous_number_taskmanagers = taskmanagers[0]
#     scaling_events = 0
#     for val in taskmanagers:
#         if val != previous_number_taskmanagers:
#             scaling_events += 1
#         previous_number_taskmanagers = val
#     return scaling_events
#
#
# def pareto_plot(experimentFiles: [ExperimentFile], xMetric=Metrics.TASKMANAGER, xMetricLimit=None,
#                 yMetric=Metrics.LATENCY, yMetricLimit=None, saveDirectory=None, saveName=None):
#     autoscaler_layout = {
#         Autoscalers.HPA: ("red", "o"),  # (color, marker)
#         Autoscalers.VARGA1: ("purple", "*"),
#         Autoscalers.VARGA2: ("orange", "P"),
#         Autoscalers.DHALION: ("green", "X"),
#         Autoscalers.DS2_ORIGINAL: ("pink", "D"),
#         Autoscalers.DS2_UPDATED: ("brown", "s"),
#     }
#
#     xMetric_values = []
#     yMetric_values = []
#     seen_autoscalers = []
#     texts = []
#     fig, ax = plt.subplots()
#     for experimentFile in experimentFiles:
#         xMetric_avg = getAverageMetric(experimentFile, xMetric)
#         xMetric_values.append(xMetric_avg)
#
#         yMetric_avg = getAverageMetric(experimentFile, yMetric)
#         yMetric_values.append(yMetric_avg)
#
#         if xMetricLimit and xMetric_avg > xMetricLimit:
#             continue
#         if yMetricLimit and yMetric_avg > yMetricLimit:
#             continue
#
#         autoscaler = experimentFile.getAutoscaler()
#         color, marker = autoscaler_layout[experimentFile.getAutoscaler()]
#
#         legend_label = f"{autoscaler}" if autoscaler not in seen_autoscalers else ""
#         ax.scatter(xMetric_avg, yMetric_avg, s=50, color=color, marker=marker, label=legend_label)
#         seen_autoscalers.append(autoscaler)
#         texts.append(ax.text(xMetric_avg, yMetric_avg, experimentFile.getVariable(), ha='right', va='top', size=10))
#
#     if xMetricLimit:
#         plt.xlim((0, xMetricLimit))
#     if yMetricLimit:
#         plt.ylim((0, yMetricLimit))
#
#     # if zoomed:
#     #     plt.ylim([0,zoomed_latency_limit])
#     #     plt.xlim([0,16])
#     # else:
#     #     plt.ylim([0,latency_limit])
#     #     plt.xlim([0,16])
#
#     plt.legend(loc=(1.02, 0.5), labelspacing=1)
#     plt.grid()
#     # todo: create better axis titles
#     plt.xlabel(f"Average {xMetric}")
#     plt.ylabel(f"Average {yMetric}")
#
#     adjust_text(texts, only_move={'points': 'y', 'texts': 'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0))
#
#     if saveDirectory and saveName:
#         savePlot(plt, saveDirectory, saveName, bbox_inches=Bbox([[0, 0], [8.0, 5.0]]), dpi=600)
#         plt.close()
#     else:
#         plt.show()

def plotDataFile(
        file: ExperimentFile,
        save_directory=None,
        experiment_name=None,
        metrics=None,
        # metric_ranges: {str, (float, float)} = None,
):
    """
    Create a plot of a datafile with the provided metrics
    :param file: ExperimentFile to plot
    :param save_directory: directory to save the plot in. If left None, the plot is only shown.
    :param experiment_name: name of the experiment to create a plot from
    :param metrics: Metrics to visualise in the plot. if left None, all available metrics will be used.
    :return: None
    """
    if not file:
        print(f"Error: no datafile found.")

    if metrics is None:
        metrics = Metrics.get_all_metric_classes()

    data = pd.read_csv(file.file_path)
    time_column = data["minutes"]

    stylePlots()
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    fig.suptitle(f"Plot of {experiment_name}")

    for i in range(len(metrics)):

        # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
        metricName = metrics[i]
        metric_column = getMetricColumn(metricName, data)
        if metric_column is None:
            continue

        # Interpolate and fill NaN with 0
        metric_column = metric_column.interpolate()
        metric_column = metric_column.fillna(0)

        axis = axs[i] if len(metrics) > 1 else axs

        # yLim_min, yLim_max = getYrange(metricName, min_range, max_range, metric_ranges)

        # Set axis
        axis.plot(time_column, metric_column)
        axis.title.set_text(metricName)
        max_range = 1.2 * max(metric_column)
        min_range = 1.2 * min(metric_column)
        axis.set_ylim([min_range, max_range])
        axis.grid()

        # Set xlabel on final subplot
        if i == len(metrics) - 1:
            axis.set_xlabel("Minutes")

    if save_directory and experiment_name:
        savePlot(plt, save_directory, experiment_name)
        plt.close()
    else:
        plt.show()


# def scatterPlotDataFrame(
#         file: ExperimentFile,
#         save_directory=None,
#         experiment_name=None,
#         metrics=None,
#         # metric_ranges: {str, (float, float)} = None,
# ):
#     """
#     Create a plot of a datafile with the provided metrics
#     :param metric_ranges:
#     :param saveDirectory: directory to save the plot in. If left None, the plot is only shown.
#     :param file: Datafile to create a plot from
#     :param metrics: Metrics to visualise in the plot. if left None, all available metrics will be used.
#     :return: None
#     """
#     if metric_ranges is None:
#         metric_ranges = []
#
#     if not file:
#         print(f"Error: no datafile found.")
#
#     if metrics is None:
#         metrics = Metrics.get_all_metric_classes()
#
#     data = pd.read_csv(file.file_path)
#     # data = removeNaNFromDataframe(data)
#
#     stylePlots()
#     fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
#     fig.suptitle(f"Scatter-plot of {experiment_name}")
#     fig.subplots_adjust(hspace=.5, wspace=.001)
#     for i in range(len(metrics)):
#
#         # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
#         metricName = metrics[i]
#         metric_column = getMetricColumn(metricName, data)
#         metric_column = metric_column.dropna()
#
#         axis = axs[i] if len(metrics) > 1 else axs
#
#         max_range = 1.2 * max(metric_column)
#         min_range = 1.2 * min(metric_column)
#         yLim_min, yLim_max = getYrange(metricName, min_range, max_range, metric_ranges)
#
#         # Set axis
#         axis.scatter(metric_column.index, metric_column, marker=".", linewidth=1)
#
#         axis.title.set_text(metricName)
#         axis.set_ylim([yLim_min, yLim_max])
#         axis.grid()
#
#         # Set xlabel on final subplot
#         if i == len(metrics) - 1:
#             axis.set_xlabel("Index (0 - 140 minutes)")
#
#     if save_directory and experiment_name:
#         savePlot(plt, save_directory, experiment_name)
#         plt.close()
#     else:
#         plt.show()