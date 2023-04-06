import argparse

from DataClasses import FileManager
from ParameterProcessing import SingleFolderPlotParameters
from Plotting import Plotter


def plotIndividualExperiments(parameters: SingleFolderPlotParameters):
    experimentFiles = parameters.fetch_experiment_files_from_combined_data_folder()
    for experimentFile in experimentFiles:
        experiment_save_name = FileManager.get_plot_filename(
            experimentFile.get_experiment_name(), parameters.get_plot_postfix_label())
        Plotter.plot_experiment_file(
            experiment_file=experimentFile,
            metric_names=parameters.get_metrics(),
            metric_ranges=parameters.getMetricRanges(),
            result_filetype=parameters.get_result_filetype(),
            save_directory=parameters.get_plot_save_folder(),
            experiment_name=experiment_save_name,
        )


def parseArguments():
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("individual-plots")

    # Parse arguments
    parser = argparse.ArgumentParser(description='Plot individual experiments')
    parameters.include_arguments_in_parser(parser)

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetch_arguments_from_namespace(namespace)

    # Call plot function
    plotIndividualExperiments(parameters)


if __name__ == "__main__":
    parseArguments()
