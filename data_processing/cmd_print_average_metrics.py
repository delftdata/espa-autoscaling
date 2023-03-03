import argparse

from tabulate import tabulate
from Plotting import DataProcessor, PlotWriter
from ParameterProcessing import SingleFolderPlotParameters





def printAverageData(parameters: SingleFolderPlotParameters, add_metrics_average: bool, add_metrics_percentile_50,
                     add_metrics_percentile_95, add_metrics_maximum: bool, custom_metrics_percentile: int = None, postfix_label: str = None):

    def round_results(results: [float]) -> [float]:
        """
        For the results, round all values > 1 on 1 decimal. All values < 1 round it on 3 decimals
        :param results: List of floats to round.
        :return: List of rounded floats.
        """
        return list(map(lambda v: round(v, 3) if v < 1 else round(v, 1), results))

    experiment_files = parameters.fetch_experiment_files_from_combined_data_folder()
    experiment_file_datafile_mapping = DataProcessor.get_experiment_dataframe_mapping(experiment_files)
    metric_names = parameters.get_metrics()
    metric_names = DataProcessor.get_shared_metrics_from_dataframes(metric_names, experiment_file_datafile_mapping.values())

    table = [["Experiment"] + metric_names]

    file_name = f"{postfix_label}_" if postfix_label else ""
    file_name = file_name + "data_summary"
    file_name = f"{file_name}_avg" if add_metrics_average else file_name
    file_name = f"{file_name}_prc{custom_metrics_percentile}" if custom_metrics_percentile else file_name
    file_name = f"{file_name}_prc50" if add_metrics_percentile_50 else file_name
    file_name = f"{file_name}_prc95" if add_metrics_percentile_95 else file_name
    file_name = f"{file_name}_max" if add_metrics_maximum else file_name

    percentiles = [custom_metrics_percentile] if custom_metrics_percentile is not None else []
    percentiles = percentiles + [50] if add_metrics_percentile_50 else percentiles
    percentiles = percentiles + [95] if add_metrics_percentile_95 else percentiles
    for experiment_file, data_frame in experiment_file_datafile_mapping.items():
        if add_metrics_average:
            avg_results = DataProcessor.get_average_metrics_from_dataframe(data_frame, metric_names)
            avg_results = round_results(avg_results)
            avg_row = [experiment_file.get_experiment_name() + "(avg)"] + avg_results
            table.append(avg_row)
        for percentile in percentiles:
            percentile_results = DataProcessor.get_percentile_metrics_from_dataframe(data_frame, metric_names, percentile)
            percentile_results = round_results(percentile_results)
            percentile_row = [experiment_file.get_experiment_name() + f"(pct_{percentile})"] + percentile_results
            table.append(percentile_row)
        if add_metrics_maximum:
            max_results = DataProcessor.get_maximum_metrics_from_dataframe(data_frame, metric_names)
            max_results = round_results(max_results)
            max_row = [experiment_file.get_experiment_name() + "(max)"] + max_results
            table.append(max_row)

    table_result = tabulate(table)
    print(table_result)
    PlotWriter.save_data(
        save_directory=parameters.get_plot_save_folder(),
        save_name=file_name,
        data_string=table_result,
        extension=parameters.get_result_filetype()
    )


def parseArguments():
    # Create SingleFolderPlotParameters without a result folder and thresholds_option
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("data_summary", "txt")

    # Parse arguments
    parser = argparse.ArgumentParser(description="Output an aggregated version of the selected experiments. Possible "
                                                 "aggregations: maximum, average")
    parameters.include_arguments_in_parser(parser)

    parser.add_argument('--add_maximum_metrics', action='store_true')
    parser.add_argument('--add_average_metrics', action='store_true')
    parser.add_argument('--add_percentile_50_metrics', action='store_true')
    parser.add_argument('--add_percentile_95_metrics', action='store_true')
    parser.add_argument('--add_custom_percentile', type=int)


    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetch_arguments_from_namespace(namespace)

    add_average_metrics = True if namespace.add_average_metrics else False
    add_metrics_percentile_50 = True if namespace.add_percentile_50_metrics else False
    add_metrics_percentile_95 = True if namespace.add_percentile_95_metrics else False
    add_maximum_metrics = True if namespace.add_maximum_metrics else False

    postfix_label = parameters.get_plot_postfix_label()

    custom_percentile = None
    if namespace.add_custom_percentile:
        custom_percentile = namespace.add_custom_percentile
        if custom_percentile not in range(0, 101):
            print("Please provide a custom percentile between 0 and 101.")
            return
    # Call plot function
    printAverageData(parameters, add_average_metrics, add_metrics_percentile_50, add_metrics_percentile_95, add_maximum_metrics,
                     custom_metrics_percentile=custom_percentile, postfix_label=postfix_label)


if __name__ == "__main__":
    parseArguments()
