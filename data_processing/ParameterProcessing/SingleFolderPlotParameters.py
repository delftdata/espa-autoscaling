from .PlotParameters import PlotParameters
from DataClasses import FileManager, ExperimentFileGenerator
import argparse


class SingleFolderPlotParameters(PlotParameters):
    # main_folder is the root of the project.
    __main_folder = ""

    # plot_folder_name is the folder where to save the result. This is saved at {graph_folder}/{graph_folder_name}
    __plot_folder_name: str
    # plot postfix label is a postfix for the filename. {name}_{graph_postfix_label}
    __plot_postfix_label = ""

    # Whether to create a scatter_plot or a regular plot
    __create_scatter_plot = False
    __option_create_scatter_plot = False

    def __init__(self, default_graph_folder_name: str, option_create_scatter_plot=False):
        super().__init__()
        self.__graph_folder_name = default_graph_folder_name
        self.__option_create_scatter_plot = option_create_scatter_plot

    # getter and setter for main_folder
    def get_main_folder(self) -> str:
        """
        Get main_folder
        """
        return self.__main_folder

    def __set_main_folder(self, main_folder: str):
        """
        Set main_folder to main_folder
        """
        self.__main_folder = main_folder

    # getter and setter for __plot_folder_name
    def get_plot_folder_name(self) -> str:
        """
        Get plot_folder_name
        """
        return self.__plot_folder_name

    def __set_plot_folder_name(self, plot_folder_name: str):
        """
        Set plot_folder_name to plot_folder_name
        """
        self.__plot_folder_name = plot_folder_name

    # getter and setter for plot_postfix_label
    def get_plot_postfix_label(self) -> str:
        """
        Get plot_postfix_label
        """
        return self.__plot_postfix_label

    def __set_plot_postfix_label(self, plot_postfix_label: str):
        """
        Set plot_postfix_label to plot_postfix_label
        """
        self.__plot_postfix_label = plot_postfix_label

    # getter and setter for create_scatter_plot
    def get_create_scatter_plot(self) -> bool:
        """
        Get create_scatter_plot
        """
        return self.__create_scatter_plot

    def __set_create_scatter_plot(self, create_scatter_plot: bool):
        """
        Set create_scatter_plot if its option is enabled.
        Else keep it at its default value.
        """
        if self.__option_create_scatter_plot:
            self.create_scatter_plot = create_scatter_plot

    def fetch_experiment_files_from_combined_data_folder(self):
        """
        Fetch all experiment files with the specified queries, autoscalers, modes and tags from the combined_data_folder
        found in main_folder.
        """
        combined_data_folder = FileManager.get_combined_data_folder(self.__main_folder)
        return ExperimentFileGenerator.get_specific_experiment_files_from_combined_data_folder(
            combined_data_folder, self.get_queries(), self.get_autoscalers(), self.get_modes(), self.get_tags)

    def include_arguments_in_parser(self, argument_parser: argparse.ArgumentParser):
        """
        Included single-folder specific data to the parser
        """
        super().include_arguments_in_parser(argument_parser)

        def include_main_folder_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('main_directory', type=str,
                                help="Main directory containing all information fetched from experiments. Data is saved at"
                                     "main_directory/data and combined_data is saved at main_directory/data/combined_data."
                                     "Graphs will be saved at main_directory/graphs")

        def include_plot_folder_name_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument("--plot_folder_name", type=str, nargs="?",
                                help=f"Define the name of the directory the plots will be saved in. This directory will "
                                     f"be placed in main_directory/graphs/[plot_folder_name]. "
                                     f"Default={self.get_plot_folder_name()}")

        def include_plot_postfix_label_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument("--plot_postfix_label", type=str, nargs="?",
                                help=f"Add a postfix to the filename of the generated plots. "
                                     f"Default={self.get_plot_postfix_label()}")

        def include_create_scatter_plot_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('--create_scatter_plot', action='store_true',
                                help=f"Add argument to create a scatter-plot of the data instead of a regular plot")

        include_main_folder_in_parser(argument_parser)
        include_plot_folder_name_in_parser(argument_parser)
        include_plot_postfix_label_in_parser(argument_parser)
        if self.__option_create_scatter_plot:
            include_create_scatter_plot_in_parser(argument_parser)

    def fetch_arguments_from_namespace(self, namespace: argparse.Namespace):
        """
        Fetch single-folder-specific-data from the namespace parser
        """
        super().fetch_arguments_from_namespace(namespace)

        def fetch_main_folder_from_namespace(args: argparse.Namespace):
            main_directory = args.main_directory
            self.__set_main_folder(main_directory)

        def fetch_plot_folder_name_from_namespace(args: argparse.Namespace):
            plot_folder_name = args.plot_folder_name
            # if plot_folder_name provided is provided
            if plot_folder_name:
                # set plot_folder_name
                self.__set_plot_folder_name(plot_folder_name)

        def fetch_plot_postfix_label_from_namespace(args: argparse.Namespace):
            plot_postfix_label = args.plot_postfix_label
            # if plot_postfix_label is provided
            if plot_postfix_label:
                # set plot_postfix_label
                self.__set_plot_postfix_label(plot_postfix_label)

        def fetch_create_scatter_plot_from_namespace(args: argparse.Namespace):
            create_scatter_plot = args.create_scatter_plot
            # if provided
            if create_scatter_plot is not None:
                self.__set_create_scatter_plot(create_scatter_plot)

        fetch_main_folder_from_namespace(namespace)
        fetch_plot_folder_name_from_namespace(namespace)
        fetch_plot_postfix_label_from_namespace(namespace)
        if self.__option_create_scatter_plot:
            fetch_create_scatter_plot_from_namespace(namespace)

