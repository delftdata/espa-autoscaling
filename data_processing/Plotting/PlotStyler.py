from matplotlib import pyplot as plt

PLT_STYLE = "seaborn-dark-palette"


def style_plots():
    plt.style.use(PLT_STYLE)


def get_y_axis_range_of_metric(metric_name, metric_column, metric_ranges):
    l_range, r_range = None, None
    if metric_name in metric_ranges:
        l_range, r_range = metric_ranges[metric_name]

        # if None, set range to 1.2 * minimum/maximum value of column
    l_range = l_range or 1.2 * min(metric_column)
    r_range = r_range or 1.2 * max(metric_column)

    return l_range, r_range
