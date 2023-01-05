import matplotlib as mpl
from matplotlib import pyplot as plt
from DataClasses import ExperimentFile
import Plotting.PlotWriter as PlotWriter
import Plotting.PlotStyler as PlotStyler
import Plotting.DataProcessor as DataProcessor


def plot_experiment_file(
        experiment_file: ExperimentFile,
        metric_names,
        metric_ranges: {str, (float, float)},
        result_filetype=None,
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

    if save_directory and experiment_name and result_filetype:
        PlotWriter.save_plot(plt, save_directory, experiment_name, extension=result_filetype)
    else:
        PlotWriter.show_plot(plt)


def plot_and_overlap_data_files(
        experiment_files: [ExperimentFile],
        metric_names: [str],
        metric_ranges: {str, (float, float)},
        result_filetype: str,
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
            axis.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08 * len(metric_names)), fancybox=True, shadow=True, ncol=5)

    if save_directory and experiment_name and result_filetype:
        PlotWriter.save_plot(plt, save_directory, experiment_name, extension=result_filetype)
    else:
        PlotWriter.show_plot(plt)


def _add_individual_metric_plot_to_axis(axis, metric_name: str, data_frame, metric_ranges: {str, (float, float)},
                                        add_time_unit: bool, title_label=None, title_size=None, label_size=None):
    time_column = DataProcessor.get_time_column_from_data_frame(data_frame)
    data_column = DataProcessor.getMetricColumn(metric_name, data_frame)
    data_column = DataProcessor.interpolate_data_column(data_column)

    # Set y-axis ranges
    l_range, r_range = PlotStyler.get_y_axis_range_of_metric(metric_name, data_column, metric_ranges)

    __add_individual_plot(metric_name, axis, time_column, data_column, (l_range, r_range), add_time_unit,
                          title_label=title_label, title_size=title_size, label_size=label_size)



def __add_individual_plot(metric_name, axis, time_column, data_column, value_range: (float, float),
                          add_time_unit: bool, title_label=None, title_size=None, label_size=None):

    # Set x and y axis
    axis.plot(time_column, data_column)

    axis.set_ylim([value_range[0], value_range[1]])
    axis.grid()

    # Set titles of axis
    PlotStyler.set_axis_titles(axis, metric_name, add_unit_to_y_axis=False,
                               add_time_unit=add_time_unit,
                               titel_label=title_label,
                               title_size=title_size, label_size=label_size)

def plot_multiple_data_files_in_single_file(
        experiment_files: [ExperimentFile],
        constant_metric_names: [str],
        metric_names: [str],
        metric_ranges: {str, (float, float)},
        result_filetype: str,
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

    TITLE_SIZE = 16
    LABEL_SIZE = 16
    TICK_SIZE = 15
    tmp_factor = 3
    FIG_SIZE = (4.2 * tmp_factor, 1.8 * tmp_factor)

    PlotStyler.style_plots(tick_size=TICK_SIZE, title_size=TITLE_SIZE, label_size=LABEL_SIZE)

    # Create pyplot and style it

    total_subplots = len(constant_metric_names) + len(metric_names) * len(experiment_files)
    fig, axs = plt.subplots(total_subplots, 1, figsize=FIG_SIZE, facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    axis_index = 0


    # Pick first datafile to
    constant_metric_experiment_file, constant_data_frame = list(experiment_file_data_file_mapping.items())[0]
    print(f"Using the data of {constant_metric_experiment_file.get_experiment_name()} to plot constant metrics {constant_metric_names}")
    for i in range(len(constant_metric_names)):
        # metric name
        metric_name = constant_metric_names[i]

        # axis to plot on
        axis = axs[axis_index] if total_subplots > 1 else axs
        axis_index += 1

        # Whether to plot the time unit on the x-axis
        plot_x_axis_unit = axis_index == total_subplots

        # Plot data
        _add_individual_metric_plot_to_axis(axis, metric_name, constant_data_frame, metric_ranges, plot_x_axis_unit)

    for i in range(len(metric_names)):
        metric_name = metric_names[i]
        for experiment_file, data_frame in experiment_file_data_file_mapping.items():

            # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
            axis = axs[axis_index] if total_subplots > 1 else axs
            axis_index += 1

            # Whether to plot the time unit on the x-axis
            plot_x_axis_unit = axis_index == total_subplots

            # Add plot
            _add_individual_metric_plot_to_axis(axis, metric_name, data_frame, metric_ranges, plot_x_axis_unit,
                                                title_label=experiment_file.get_autoscaler())


    if save_directory and experiment_name and result_filetype:
        PlotWriter.save_plot(plt, save_directory, experiment_name, extension=result_filetype)
    else:
        PlotWriter.show_plot(plt)

