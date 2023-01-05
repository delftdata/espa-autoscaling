import matplotlib as mpl
from matplotlib import pyplot as plt
from DataClasses import Metrics

PLT_STYLE = "seaborn-dark-palette"


def style_plots(tick_size=None, title_size=None, label_size=None):
    plt.style.use(PLT_STYLE)
    # Set tick_size of plot
    if tick_size:
        __set_tick_size(tick_size)
    if title_size:
        __set_title_size(title_size)
    if label_size:
        __set_label_size(label_size)


def __set_tick_size(tick_size):
    mpl.rcParams['xtick.labelsize'] = tick_size
    mpl.rcParams['ytick.labelsize'] = tick_size


def __set_title_size(title_size):
    mpl.rcParams['font.size'] = title_size


def __set_label_size(label_size):
    mpl.rcParams['axes.labelsize'] = label_size



def get_y_axis_range_of_metric(metric_name, metric_column, metric_ranges):
    l_range, r_range = None, None
    if metric_name in metric_ranges:
        l_range, r_range = metric_ranges[metric_name]

        # if None, set range to 1.2 * minimum/maximum value of column
    l_range = l_range or 1.2 * min(metric_column)
    r_range = r_range or 1.2 * max(metric_column)

    return l_range, r_range



def set_axis_titles(axis, metric_name, add_unit_to_y_axis=True, add_time_unit=True, titel_label=None, title_size=None,
                    label_size=None):
    """
    Set title on the axis
    :param tick_size: Fontsize of ticks. Not set when None
    :param label_size: Fontsize of labels. Not set when None
    :param title_size: Fontsize of title. Not set when None
    :param titel_label: Additional label to place in front of the title
    :param axis: axis to set the title on
    :param metric_name: name of the metric shown in the plot
    :param add_unit_to_y_axis: whether to add the unit in the y-axis or in the title of the plot
    :param add_time_unit: whether to add the timeunit in the x-axis
    """
    __add_title(axis, metric_name, not add_unit_to_y_axis, titel_label, title_size=title_size)
    if add_unit_to_y_axis:
        __add_unit_to_y_axis(axis, metric_name, label_size=label_size)
    if add_time_unit:
        __add_unit_to_x_axis(axis, label_size=label_size)



def __add_title(axis, metric_name: str, add_unit: bool=False, titel_label=None, title_size=None):
    """
    Add title to axis
    :param axis: Axis to add title too
    :param metric_name: Metric_name of the axis where to set the title
    :param add_unit: Whether to add the metric's unit to the title
    :return: None
    """
    title = Metrics.get_title_of_metric(metric_name)
    if add_unit:
        metric_unit = Metrics.get_unit_of_metric(metric_name)
        metric_unit_title = f" ({metric_unit})" if metric_unit else ""
        title = f"{title}{metric_unit_title}"
    if titel_label:
        title = f"{titel_label} - {title}"
    title = title.capitalize()
    axis.title.set_text(title)
    if title_size:
        axis.title.set_size(title_size)





def __add_unit_to_y_axis(axis, metric_name, label_size=None):
    if label_size:
        axis.yaxis.label.set_size(label_size)
    metric_unit = Metrics.get_unit_of_metric(metric_name)
    axis.set_ylabel(metric_unit)


def __add_unit_to_x_axis(axis, label_size=None):

    axis.set_xlabel("Minutes")



