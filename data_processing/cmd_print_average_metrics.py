import argparse

from tabulate import tabulate
from Plotting import DataProcessor, PlotWriter
from ParameterProcessing import SingleFolderPlotParameters


def printAverageData(parameters: SingleFolderPlotParameters, add_metrics_average: bool, add_metrics_maximum: bool):

    experiment_files = parameters.fetch_experiment_files_from_combined_data_folder()
    experiment_file_datafile_mapping = DataProcessor.get_experiment_dataframe_mapping(experiment_files)
    metric_names = parameters.get_metrics()
    metric_names = DataProcessor.get_shared_metrics_from_dataframes(metric_names, experiment_file_datafile_mapping.values())

    table = [["Experiment"] + metric_names]

    file_name = "data_summary"
    file_name = f"{file_name}_avg" if add_metrics_average else file_name
    file_name = f"{file_name}_max" if add_metrics_maximum else file_name

    for experiment_file, data_frame in experiment_file_datafile_mapping.items():
        if add_metrics_average:
            avg_results = DataProcessor.get_average_metrics_from_dataframe(data_frame, metric_names)
            avg_results = list(map(lambda v: round(v, 3) if v < 1 else round(v, 1), avg_results))
            avg_row = [experiment_file.get_experiment_name() + "(avg)"] + avg_results
            table.append(avg_row)
        if add_metrics_maximum:
            max_results = DataProcessor.get_maximum_metrics_from_dataframe(data_frame, metric_names)
            max_results = list(map(lambda v: round(v, 3) if v < 1 else round(v, 1), max_results))
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

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetch_arguments_from_namespace(namespace)

    add_average_metrics = True if namespace.add_average_metrics else False
    add_maximum_metrics = True if namespace.add_maximum_metrics else False

    # Call plot function
    printAverageData(parameters, add_average_metrics, add_maximum_metrics)


if __name__ == "__main__":
    parseArguments()
