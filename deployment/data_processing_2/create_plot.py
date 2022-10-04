import pandas as pd
import matplotlib.pyplot as plt
import Metrics

DATA_FOLDER = "./results/full_results"
RESULT_FOLDER = "./results/plots"


def plotDataFile(queryNumber="1", autoscaler="dhalion", setting="1", metrics=None, savePlot=False):
    """
    Plot all data from DATA_FOLDER and store it in RESULT_FOLDER
    :param queryNumber: number of the query to process
    :param autoscaler: autoscaler to process
    :param setting: autoscaler setting used in experiments
    :param metrics: a list of metrics to show in the plot
    :param savePlot: save the plot in RESULT_FOLDER
    :return: None
    """

    # Plot all metrics if no subset was provided
    if metrics is None:
        metrics = Metrics.getAllMetricClasses()

    source_name = f"q{queryNumber}_{autoscaler}_{setting}.csv"
    data = pd.read_csv(DATA_FOLDER + "/" + source_name)
    time_column = data["minutes"]

    # fig, axs = plt.subplots(len(metrics))
    fig, axs = plt.subplots(len(metrics), 1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace=.5, wspace=.001)
    for i in range(len(metrics)):
        metricName = Metrics.convertMetricClassestoMetricNames(metrics)[i]
        metric_column = data[metricName]
        axs[i].plot(time_column, metric_column, color="red")
        axs[i].title.set_text(metricName)

        axs[i].set_ylim([0, metric_column.max() * 1.2])
        axs[i].grid()
    axs[len(metrics) - 1].set_xlabel("Minutes")

    plt.show()


if __name__ == "__main__":
    plotDataFile()