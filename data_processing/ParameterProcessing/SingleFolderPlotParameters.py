from .PlotParameters import PlotParameters
from DataClasses import ExperimentFile
import argparse


class SingleFolderPlotParameters(PlotParameters):
    # Required
    __main_folder = "ERROR: No main folder set"
    __data_label = ""
    __result_folder_name: str
    __result_label = ""
    __plot_thresholds = False
    __create_scatter_plot = False
    __option_plot_thresholds = True
    __option_create_scatter_plot = True

    def __init__(self, default_result_folder_name: str, option_plot_thresholds=True, option_metric_ranges=True,
                 option_create_scatter_plot=False):
        super().__init__(option_metric_ranges=option_metric_ranges)
        # If default_result_folder_name == "", both result_folder and result_label will not be added to parser
        self.__result_folder_name = default_result_folder_name
        self.__option_plot_thresholds = option_plot_thresholds
        self.__option_create_scatter_plot = option_create_scatter_plot

    def setMainFolder(self, main_folder: str):
        if main_folder:
            self.__main_folder = main_folder

    def setDataLabel(self, data_label: str):
        if data_label:
            self.__data_label = data_label

    # Overwrite parent folders to make fetching the datafolder easier
    def getDataFolder(self):
        return self.getDefaultDataFolder(self.__main_folder)

    def getDataLabel(self):
        return self.__data_label

    # Overwrite parent folders to make fetching the datafolder easier
    def getGraphFolder(self):
        return self.getDefaultGraphFolder(self.__main_folder)

    # Set a custom result folder name
    def setCustomResultFolderName(self, result_folder_name: str):
        if result_folder_name:
            self.__result_folder_name = result_folder_name

    # Get ResultFolder to save the results
    def getResultFolder(self):
        return f"{self.getGraphFolder()}/{self.__result_folder_name}"

    # Set a label for the result file
    def setResultLabel(self, resultLabel: str):
        if resultLabel:
            self.__result_label = resultLabel

    def getExperimentFiles(self):
        return ExperimentFile.getAvailableExperimentFiles(self.getDataFolder(),
                                                          self.getExperimentsWithDatalabel(self.getDataLabel()))

    # Get the result label of a file
    def getResultLabel(self):
        return self.__result_label

    # Also plot result threshold
    def setPlotThreshold(self, plot_thresholds: bool):
        if plot_thresholds:
            self.__plot_thresholds = plot_thresholds

    def getPlotThresholds(self):
        return self.__plot_thresholds

    # Create a scatterplot
    def getCreateScatterPlot(self):
        return self.__create_scatter_plot

    def setCreateScatterPlot(self, create_scatter_plot: bool):
        if create_scatter_plot:
            self.__create_scatter_plot = create_scatter_plot

    def includeArgumentsInParser(self, argumentParser: argparse.ArgumentParser):
        super().includeArgumentsInParser(argumentParser)

        def includeMainFolderInParser(parser: argparse.ArgumentParser):
            parser.add_argument('source_directory', type=str,
                                help="Directory in which datafiles can be found at src_dir/full-data")

        def includeSourceLabelInParser(parser: argparse.ArgumentParser):
            parser.add_argument('-source_label', type=str, nargs="?")

        def includeResultFolderInParser(parser: argparse.ArgumentParser):
            parser.add_argument('-result_folder_name', type=str, nargs="?")

        def includeResultLabelInParser(parser: argparse.ArgumentParser):
            parser.add_argument('-result_label', type=str, nargs="?")

        def includePlotThresholds(parser: argparse.ArgumentParser):
            parser.add_argument('--plot_thresholds', action='store_true')

        def includeCreateScatterPlot(parser: argparse.ArgumentParser):
            parser.add_argument('--create_scatter_plot', action='store_true')

        includeMainFolderInParser(argumentParser)
        includeSourceLabelInParser(argumentParser)
        if self.__result_folder_name:
            includeResultFolderInParser(argumentParser)
            includeResultLabelInParser(argumentParser)

        if self.__option_plot_thresholds:
            includePlotThresholds(argumentParser)

        if self.__option_create_scatter_plot:
            includeCreateScatterPlot(argumentParser)

    def fetchArgumentsFromNamespace(self, namespace: argparse.Namespace):
        super().fetchArgumentsFromNamespace(namespace)

        def fetchMainFolderFromNamespace(args: argparse.Namespace):
            src_directory = args.source_directory
            self.setMainFolder(src_directory)

        def fetchSourceLabelFromNamespace(args: argparse.Namespace):
            src_label = args.source_label
            self.setDataLabel(src_label)

        def fetchResultFolderFromNamespace(args: argparse.Namespace):
            result_folder = args.result_folder_name
            if result_folder:
                self.setCustomResultFolderName(result_folder)

        def fetchResultLabelFromNamespace(args: argparse.Namespace):
            result_label = args.result_label
            if result_label:
                self.setResultLabel(result_label)

        def fetchPlotThresholds(args: argparse.Namespace):
            self.setPlotThreshold(args.plot_thresholds)

        def fetchCreateScatterPlot(args: argparse.Namespace):
            self.setCreateScatterPlot(args.create_scatter_plot)

        fetchMainFolderFromNamespace(namespace)
        fetchSourceLabelFromNamespace(namespace)

        if self.__result_folder_name:
            fetchResultFolderFromNamespace(namespace)
            fetchResultLabelFromNamespace(namespace)

        if self.__option_plot_thresholds:
            fetchPlotThresholds(namespace)

        if self.__option_create_scatter_plot:
            fetchCreateScatterPlot(namespace)

