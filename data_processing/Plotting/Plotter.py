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

    metric_names = DataProcessor.filter_out_missing_metric_names(metric_names, data_frame)

    time_column = DataProcessor.get_time_column_from_data_frame(data_frame)

    PlotStyler.style_plots()
    fig, axs = plt.subplots(len(metric_names), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    fig.suptitle(f"Plot of {experiment_name}")

    for i in range(len(metric_names)):
        metric_name = metric_names[i]

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

        # Set titles of axis
        PlotStyler.set_axis_titles(axis, metric_name, add_unit_to_y_axis=False, add_time_unit=i == len(metric_names) - 1)

    if save_directory and experiment_name:
        PlotWriter.savePlot(plt, save_directory, experiment_name)
    else:
        PlotWriter.showPlot(plt)


def plot_and_overlap_data_files(
        experiment_files: [ExperimentFile],
        metric_names: [str],
        metric_ranges: {str, (float, float)},
        save_directory=None,
        experiment_name=None
):
    experiment_file_data_file_mapping = {}
    for experiment_file in experiment_files:
        # get data_frame of experiment_file
        data_frame = DataProcessor.get_data_frame(experiment_file)
        # add data_frame to experiment_file data_file_mapping
        experiment_file_data_file_mapping[experiment_file] = data_frame
        # filter out metrics that are not present in the data_frame
        metric_names = DataProcessor.filter_out_missing_metric_names(metric_names, data_frame)


    PlotStyler.style_plots()
    # Create pyplot and style it
    fig, axs = plt.subplots(len(metric_names), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)

    # For every metric
    for i in range(len(metric_names)):
        metric_name = metric_names[i]
        axis = axs[i] if len(metric_names) > 1 else axs

        # Make a list of all metric_information for determining the plot ranges
        all_metric_columns = None

        # Plot every datafile in the graph
        for experiment_file, data_frame in experiment_file_data_file_mapping.items():
            time_column = data_frame["minutes"]
            metric_column = DataProcessor.getMetricColumn(metric_name, data_frame)
            metric_column = DataProcessor.interpolate_data_column(metric_column)

            all_metric_columns = metric_column + all_metric_columns if all_metric_columns is not None else metric_column
            line, = axis.plot(time_column, metric_column)

            experiment_label = experiment_file.get_experiment_name()
            line.set_label(experiment_label)


        PlotStyler.set_axis_titles(axis, metric_name, False, i == len(metric_names) - 1)
        # Style graph and set title of the graph

        l_range, r_range = PlotStyler.get_y_axis_range_of_metric(metric_name, all_metric_columns, metric_ranges)
        axis.set_ylim([l_range, r_range])
        axis.grid()

        # Finalise plot style when handling the last metric
        if i == len(metric_names) - 1:
            if len(metric_names) > 1:
                axis.legend(loc='lower right', bbox_to_anchor=(1.11, -0.2))
            else:
                axis.legend(loc='lower right', bbox_to_anchor=(1.12, 0))

    if save_directory and experiment_name:
        PlotWriter.savePlot(plt, save_directory, experiment_name)
    else:
        PlotWriter.showPlot(plt)
