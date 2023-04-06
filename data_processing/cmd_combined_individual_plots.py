import argparse
from DataClasses import Experiment, Metrics, FileManager
from ParameterProcessing import SingleFolderPlotParameters
from Plotting import Plotter
from helperfunctions import get_buckets_of_similar_experiments

experiment_characteristics = ["query", "autoscaler", "mode", "tag"]



def plotMultipleExperimentsAtOnce(parameters: SingleFolderPlotParameters, ignore_experiment_characteristics: [str], constant_metrics: [str]):
    ignore_query: bool = "query" in ignore_experiment_characteristics
    ignore_autoscaler: bool = "autoscaler" in ignore_experiment_characteristics
    ignore_mode: bool = "mode" in ignore_experiment_characteristics
    ignore_tag: bool = "tag" in ignore_experiment_characteristics

    experiment_files = parameters.fetch_experiment_files_from_combined_data_folder()
    similar_experiment_files_buckets = get_buckets_of_similar_experiments(experiment_files, ignore_query,
                                                                          ignore_autoscaler, ignore_mode, ignore_tag)

    for similar_experiment_files_bucket in similar_experiment_files_buckets:
        first_experiment_file = similar_experiment_files_bucket[0]
        query = first_experiment_file.get_query() if not ignore_query else "_"
        autoscaler = first_experiment_file.get_autoscaler() if not ignore_autoscaler else "_"
        mode = first_experiment_file.get_mode() if not ignore_mode else "_"
        tag = first_experiment_file.get_tag() if not ignore_tag else "_"
        bucket_experiment_name = FileManager.get_plot_filename(
            Experiment.get_experiment_name_from_data(query, autoscaler, mode, tag),
            parameters.get_plot_postfix_label()
        )

        Plotter.plot_multiple_data_files_in_single_file(
            experiment_files=similar_experiment_files_bucket,
            constant_metric_names=constant_metrics,
            metric_names=parameters.get_metrics(),
            metric_ranges=parameters.getMetricRanges(),
            result_filetype=parameters.get_result_filetype(),
            save_directory=parameters.get_plot_save_folder(),
            experiment_name=bucket_experiment_name
        )


def include_additional_arguments_in_parser(parser):
    parser.add_argument('--ignore_experiment_characteristics', nargs='*', type=str,
                        help=f"Characteristics of experiments that similar experiments are allowed to differ on"
                             f"Possible values: any subset of {experiment_characteristics}")
    parser.add_argument('--constant_metrics', nargs='*', type=str)

def fetch_additional_arguments_From_namespace(args):
    comparison_characteristics = []
    if args.ignore_experiment_characteristics:
        provided_comparison_characteristics = args.ignore_experiment_characteristics
        comparison_characteristics = SingleFolderPlotParameters.filter_out_unsupported_arguments(
            provided_comparison_characteristics, experiment_characteristics, arg_name="ignore_experiment_characteristics")

    constant_metrics = []
    if args.constant_metrics:
        provided_constant_metrics = args.constant_metrics
        constant_metrics = SingleFolderPlotParameters.filter_out_unsupported_arguments(
            provided_constant_metrics, Metrics.get_all_metrics(), arg_name="plot_metric_once"
        )

    return comparison_characteristics, constant_metrics


def parseArguments():
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("combined-plots")

    # Parse arguments
    parser = argparse.ArgumentParser(description=f"This script fetches all data from the provided folder and plots "
                                                 f"together the results of the experiments with similar "
                                                 f"characteristics: ({experiment_characteristics}). Select some "
                                                 f"characteristics with the --ignore_experiment_characteristics tags "
                                                 f"to exclude them from the similarity comparison.")
    parameters.include_arguments_in_parser(parser)
    include_additional_arguments_in_parser(parser)

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetch_arguments_from_namespace(namespace)
    ignore_experiment_characteristics, constant_metrics = fetch_additional_arguments_From_namespace(namespace)

    # Call plot function
    plotMultipleExperimentsAtOnce(parameters, ignore_experiment_characteristics, constant_metrics)


if __name__ == "__main__":
    parseArguments()
