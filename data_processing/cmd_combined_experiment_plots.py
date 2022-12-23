import argparse
from DataClasses import ExperimentFile, Experiment
from ParameterProcessing import SingleFolderPlotParameters
from Plotting import Plotter

experiment_characteristics = ["query", "autoscaler", "mode", "tag"]


def get_buckets_of_similar_experiments(experiment_files: [ExperimentFile], ignore_query: bool, ignore_autoscaler: bool,
                                       ignore_mode: bool, ignore_tag: bool) -> [[ExperimentFile]]:
    """
    Given a list of experiment_files and boolean indicating which experiment characteristics to ignore in similarity
    comparison, return a list containing lists of experiment_files that are deemed to be 'similar' to each other.
    :param experiment_files: List of ExperimentFiles
    :param ignore_query: Whether to not consider the query of the experiments in the similarity comparison.
    :param ignore_autoscaler: Whether to nto consider the autoscaler of the experiments in the similarity comparison.
    :param ignore_mode: Whether to not consider the mode of the experiments in the similarity comparison.
    :param ignore_tag: Whether to not consider the tag of the experiments in the similarity comparison
    :return: A list of lists containing similar experiment_Files
    """
    experiment_file_buckets: [[str]] = []
    for experiment_file in experiment_files:
        found_bucket = False
        experiment = experiment_file.get_experiment()
        for experiment_file_bucket in experiment_file_buckets:
            experiment_in_bucket = experiment_file_bucket[0].get_experiment()
            if experiment_in_bucket.is_similar_experiment(experiment, ignore_query, ignore_autoscaler, ignore_mode,
                                                          ignore_tag):
                experiment_file_bucket.append(experiment_file)
                found_bucket = True
                break
        if not found_bucket:
            experiment_file_buckets.append([experiment_file])
    return experiment_file_buckets


def plotCombinedExperiments(parameters: SingleFolderPlotParameters, ignore_experiment_characteristics: [str]):
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
        bucket_experiment_name = Experiment.get_experiment_name_from_data(query, autoscaler, mode, tag)

        Plotter.plot_and_overlap_data_files(
            experiment_files=similar_experiment_files_bucket,
            metric_names=parameters.get_metrics(),
            metric_ranges=parameters.getMetricRanges(),
            save_directory=parameters.get_plot_save_folder(),
            experiment_name=bucket_experiment_name
        )


def include_additional_arguments_in_parser(parser):
    parser.add_argument('--ignore_experiment_characteristics', nargs='*', type=str,
                        help=f"Characteristics of experiments that similar experiments are allowed to differ on"
                             f"Possible values: any subset of {experiment_characteristics}")


def fetch_additional_arguments_From_namespace(args):
    comparison_characteristics = []
    if args.ignore_experiment_characteristics:
        provided_comparison_characteristics = args.ignore_experiment_characteristics
        comparison_characteristics = SingleFolderPlotParameters.filter_out_unsupported_arguments(
            provided_comparison_characteristics, experiment_characteristics, arg_name="ignore_experiment_characteristics")
    return comparison_characteristics


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
    ignore_experiment_characteristics = fetch_additional_arguments_From_namespace(namespace)

    # Call plot function
    plotCombinedExperiments(parameters, ignore_experiment_characteristics)


if __name__ == "__main__":
    parseArguments()
