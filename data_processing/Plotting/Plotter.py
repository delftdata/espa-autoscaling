from matplotlib import pyplot as plt
from DataClasses import ExperimentFile, Autoscalers, Metrics
import Plotting.PlotWriter as PlotWriter
from Plotting.PlotStyler import PlotStyler
import Plotting.DataProcessor as DataProcessor


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


def _add_individual_metric_plot_to_axis(axis, metric_name: str, data_frame, metric_ranges: {str, (float, float)}, plot_styler: PlotStyler,
                                        overwrite_axis_limits=True):
    time_column = DataProcessor.get_time_column_from_data_frame(data_frame)
    data_column = DataProcessor.getMetricColumn(metric_name, data_frame)
    data_column = DataProcessor.interpolate_data_column(data_column)

    # Set y-axis ranges
    l_yrange, r_yrange = PlotStyler.get_y_axis_range_of_metric(metric_name, data_column, metric_ranges)
    l_xrange, r_xrange = PlotStyler.get_x_range_of_data_frame()

    # If no line_color provided, check if metric has a corresponding line_color (returns None if not)
    line_color = plot_styler.get_line_color()
    if line_color:
        axis.plot(time_column, data_column, color=line_color)
    else:
        axis.plot(time_column, data_column)

    # If we do not overwrite axis limits, we take the minimum for the left limit and the maximum for the right limit
    if not overwrite_axis_limits:
        cur_l_ylim, cur_r_ylim = axis.get_ylim()
        l_yrange, r_yrange = min(cur_l_ylim, l_yrange), max(cur_r_ylim, r_yrange)
        cur_l_xlim, cur_r_xlim = axis.get_xlim()
        l_xrange, r_xrange = min(cur_l_xlim, l_xrange), max(cur_r_xlim, r_xrange)

    axis.set_ylim([l_yrange, r_yrange])
    axis.set_xlim([l_xrange, r_xrange])

    axis.grid()

    # Set titles of axis
    plot_styler.set_axis_titles(axis)


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

    amount_of_subplots = len(metric_names)

    FIG_SIZE = (18, 0.9 * (1 + amount_of_subplots))
    plot_styler: PlotStyler = PlotStyler(PlotStyler.MetricUnitLocations.TITLE, figure_size=FIG_SIZE,
                                         tick_size=14, label_size=17, title_size=15)

    fig, axs = plot_styler.get_fig_and_axis(amount_of_subplots, sup_title=f"Plot of {experiment_name}")
    fig.tight_layout()

    for i in range(amount_of_subplots):
        metric_name = metric_names[i]

        # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
        axis = axs[i] if len(metric_names) > 1 else axs

        # Set plot style
        plot_styler.set_next_plot_configurations(
            metric_name=metric_name,
            # Whether to plot the time unit on the x-axis
            add_time_unit_to_x_axis= i == amount_of_subplots - 1,
            # Label of the title
            title_label=None,
            # Line color
            line_color=None,
        )

        # Plot plot
        _add_individual_metric_plot_to_axis(axis, metric_name, data_frame, metric_ranges, plot_styler)

    if save_directory and experiment_name and result_filetype:
        PlotWriter.save_plot(plt, save_directory, experiment_name, extension=result_filetype)
    else:
        PlotWriter.show_plot(plt)


def plot_multiple_data_files_in_single_file(
        experiment_files: [ExperimentFile],
        constant_metric_names: [str],
        metric_names: [str],
        metric_ranges: {str, (float, float)},
        result_filetype: str,
        save_directory=None,
        experiment_name=None,
        plot_similar_metrics_together=False,
):
    experiment_file_data_file_mapping = {}
    for experiment_file in experiment_files:
        # get data_frame of experiment_file
        data_frame = DataProcessor.get_data_frame(experiment_file)
        # add data_frame to experiment_file data_file_mapping
        experiment_file_data_file_mapping[experiment_file] = data_frame
        # filter out metrics that are not present in the data_frame
        metric_names = DataProcessor.filter_out_missing_metric_names(metric_names, data_frame)

    total_subplots = len(constant_metric_names) + len(metric_names) * (1 if plot_similar_metrics_together else len(experiment_files))

    FIG_SIZE = (12, 0.83 * (1 + total_subplots))
    plot_styler: PlotStyler = PlotStyler(PlotStyler.MetricUnitLocations.TITLE,
                                         tick_size=11, label_size=11, title_size=11, figure_size=FIG_SIZE)

    # Create pyplot and style it
    fig, axs = plot_styler.get_fig_and_axis(total_subplots)
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

        # Set plot style
        plot_styler.set_next_plot_configurations(
            metric_name=metric_name,
            # Whether to plot the time unit on the x-axis
            add_time_unit_to_x_axis=axis_index == total_subplots,
            # Label of the title
            title_label=None,
            # Line color
            line_color=Metrics.get_color_of_metric(metric_name)
        )

        # Plot data
        _add_individual_metric_plot_to_axis(axis, metric_name, constant_data_frame, metric_ranges, plot_styler)

    for i in range(len(metric_names)):
        metric_name = metric_names[i]
        for j, (experiment_file, data_frame) in enumerate(experiment_file_data_file_mapping.items()):

            # Get metricName, Column and Axis (use axs instead of axs[i] if only one metric)
            axis = axs[axis_index] if total_subplots > 1 else axs

            # If not plotting metrics together: go to next axis after every metric. Else do not do so.
            if not plot_similar_metrics_together:
                axis_index += 1

            # Set plot style
            plot_styler.set_next_plot_configurations(
                metric_name=metric_name,
                # Whether to plot the time unit on the x-axis
                add_time_unit_to_x_axis=axis_index == total_subplots,
                # Label of the title
                title_label=Autoscalers.get_title_of_autoscaler(experiment_file.get_autoscaler()),
                # Line color
                line_color=Autoscalers.get_rbg_color_of_autoscaler(experiment_file.get_autoscaler())
            )

            # Plot plot
            _add_individual_metric_plot_to_axis(axis, metric_name, data_frame, metric_ranges, plot_styler,
                                                overwrite_axis_limits=(j == 0 or not plot_similar_metrics_together))

        # If plotting similar metrics together: go to next axis after plotting all metrics in it.
        # Else we go to the next axis per metric
        if plot_similar_metrics_together:
            axis_index += 1

    if save_directory and experiment_name and result_filetype:
        PlotWriter.save_plot(plt, save_directory, experiment_name, extension=result_filetype)
    else:
        PlotWriter.show_plot(plt)

