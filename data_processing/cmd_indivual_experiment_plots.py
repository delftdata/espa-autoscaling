import argparse

from DataClasses import FileManager
from Plotting import plotDataFile
from ParameterProcessing import SingleFolderPlotParameters


def plotIndividualExperiments(parameters: SingleFolderPlotParameters):

    experimentFiles = parameters.fetch_experiment_files_from_combined_data_folder()
    for experimentFile in experimentFiles:
        experiment_save_name = FileManager.get_plot_filename(experimentFile.get_experiment_name(),
                                                             parameters.get_plot_postfix_label())

        if parameters.get_create_scatter_plot():
            pass
            # Create a scatter plot of the data
            # scatterPlotDataFrame(
            #     file=experimentFile,
            #     saveDirectory=parameters.getResultFolder(),
            #     saveName=experiment_save_name,
            #     metrics=parameters.get_metrics()
            # )
        else:
            # Create a normal plot of the data
            plotDataFile(
                file=experimentFile,
                save_directory=parameters.get_plot_save_folder(),
                experiment_name=experiment_save_name,
                metrics=parameters.get_metrics()
            )

def parseArguments():
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("individual-plots",
                                                                        option_create_scatter_plot=True)

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
