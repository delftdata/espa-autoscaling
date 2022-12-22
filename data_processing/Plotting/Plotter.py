from matplotlib import pyplot as plt
from DataClasses import ExperimentFile
import Plotting.PlotWriter as PlotWriter
import Plotting.PlotStyler as PlotStyler
import Plotting.DataProcessor as DataProcessor


def plot_experiment_file(
        experiment_file: ExperimentFile,
        metric_names,
        metric_ranges: {str, (float, float)},
        save_directory=None,
        experiment_name=None
):
    data_frame = DataProcessor.get_data_frame(experiment_file)

    time_column = DataProcessor.get_time_column_from_data_frame(data_frame)

    PlotStyler.style_plots()
    fig, axs = plt.subplots(len(metric_names), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    fig.suptitle(f"Plot of {experiment_name}")

    for i in range(len(metric_names)):
        metric_name = metric_names[i]
        if metric_name not in data_frame:
            print(f"Warning: could not find {metric_name} in data_frame of experiment {experiment_name}. Skipping metric.")
            continue

        # Fetch data from data column
        metric_column = DataProcessor.getMetricColumn(metric_name, data_frame)
        metric_column = DataProcessor.interpolate_data_column(metric_column)

        # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
        axis = axs[i] if len(metric_names) > 1 else axs

        # Set x and y axis
        axis.plot(time_column, metric_column)

        # Set y-axis ranges
        l_range, r_range = PlotStyler.get_y_axis_range_of_metric(metric_name, metric_column, metric_ranges)
        axis.set_ylim([l_range, r_range])
        axis.grid()

        # Set metric_name as title of axis
        axis.title.set_text(metric_name)

        # Set x_label on final subplot
        if i == len(metric_names) - 1:
            axis.set_xlabel("Minutes")

    if save_directory and experiment_name:
        PlotWriter.savePlot(plt, save_directory, experiment_name)
    else:
        PlotWriter.showPlot(plt)
