import matplotlib as mpl
from matplotlib import pyplot as plt
from DataClasses import Metrics
from enum import Enum

class PlotStyler:
    PLT_STYLE = "seaborn-dark-palette"
    FIGURE_SIZE: [float]

    # Initial styling data
    TICK_SIZE: int
    TITLE_SIZE: int
    LABEL_SIZE: int

    # Multi plot data
    class MetricUnitLocations(Enum):
        TITLE = "title"
        Y_AXIS = "y-axis"
        HIDDEN = "hidden"
    METRIC_UNIT_LOCATION: MetricUnitLocations

    # Repeating plot configurations
    __next_metric_name: str
    __next_add_time_unit_to_x_axis: bool
    __next_title_label: str = None
    __next_line_color: str = None

    def __init__(self, metric_unit_location=MetricUnitLocations.TITLE,
                 tick_size=None, title_size=None, label_size=None, figure_size=None):
        self.TICK_SIZE = tick_size
        self.TITLE_SIZE = title_size
        self.LABEL_SIZE = label_size
        self.METRIC_UNIT_LOCATION = metric_unit_location
        self.FIGURE_SIZE = figure_size

        self.initialize_style()


    def initialize_style(self):
        plt.style.use(self.PLT_STYLE)
        # Set tick_size of plot
        if self.TICK_SIZE:
            self.__set_tick_size(self.TICK_SIZE)
        if self.TITLE_SIZE:
            self.__set_title_size(self.TITLE_SIZE)
        if self.LABEL_SIZE:
            self.__set_label_size(self.LABEL_SIZE)

    def get_fig_and_axis(self, number_of_subplots, sup_title=None):
        if self.FIGURE_SIZE:
            fig, axs = plt.subplots(number_of_subplots, 1, figsize=self.FIGURE_SIZE, facecolor='w', edgecolor='k', sharex='all')
        else:
            fig, axs = plt.subplots(number_of_subplots, 1, facecolor='w', edgecolor='k', sharex='all')
        fig.subplots_adjust(hspace=.5, wspace=.001)
        if sup_title:
            fig.suptitle(sup_title)
        return fig, axs

    def set_next_plot_configurations(self, metric_name, add_time_unit_to_x_axis, title_label=None, line_color=None):
        self.__next_metric_name = metric_name
        self.__next_add_time_unit_to_x_axis = add_time_unit_to_x_axis
        self.__next_title_label = title_label
        self.__next_line_color = line_color

    def get_line_color(self):
        return self.__next_line_color

    @staticmethod
    def __set_tick_size(tick_size):
        mpl.rcParams['xtick.labelsize'] = tick_size
        mpl.rcParams['ytick.labelsize'] = tick_size


    @staticmethod
    def __set_title_size(title_size):
        mpl.rcParams['font.size'] = title_size

    @staticmethod
    def __set_label_size(label_size):
        mpl.rcParams['axes.labelsize'] = label_size


    @staticmethod
    def get_y_axis_range_of_metric(metric_name, metric_column, metric_ranges):
        l_range, r_range = None, None
        if metric_name in metric_ranges:
            l_range, r_range = metric_ranges[metric_name]

            # if None, set range to 1.2 * minimum/maximum value of column
        l_range = l_range or 1.2 * min(metric_column)
        r_range = r_range or 1.2 * max(metric_column)

        return l_range, r_range

    @staticmethod
    def get_x_range_of_data_frame():
        return 0, 140


    def set_axis_titles(self, axis):
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
        # Set title
        self.__add_title(axis)

        # If we add the metric unit to the y-axis
        if self.METRIC_UNIT_LOCATION == self.MetricUnitLocations.Y_AXIS:
            self.__add_unit_to_y_axis(axis)

        # If we add the time unit to the x-axis
        if self.__next_add_time_unit_to_x_axis:
            self.__add_unit_to_x_axis(axis)

    def __add_unit_to_y_axis(self, axis):
        metric_unit = Metrics.get_unit_of_metric(self.__next_metric_name)
        axis.set_ylabel(metric_unit)


    def __add_unit_to_x_axis(self, axis):
        axis.set_xlabel("Minutes")


    def __add_title(self, axis):
        """
        Add title to axis
        :param axis: Axis to add title too
        :param metric_name: Metric_name of the axis where to set the title
        :param add_unit: Whether to add the metric's unit to the title
        :return: None
        """
        title = Metrics.get_title_of_metric(self.__next_metric_name)

        if self.METRIC_UNIT_LOCATION == self.MetricUnitLocations.TITLE:
            metric_unit = Metrics.get_unit_of_metric(self.__next_metric_name)
            metric_unit_title = f" ({metric_unit})" if metric_unit else ""
            title = f"{title}{metric_unit_title}"

        if self.__next_title_label:
            title = f"{ self.__next_title_label} - {title}"
        axis.title.set_text(title)





