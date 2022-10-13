import argparse

from src.helperclasses import ExperimentFile, Experiment, Queries, Autoscalers, Metrics
from src.plotting import plotDataFile


class PlotParameters:
    # Overall queries, autoscalers, metrics
    __queries = Queries.getAllQueries()
    __autoscalers = Autoscalers.getAllAutoscalers()
    __metrics = Metrics.getAllMetricClasses()

    def setQueries(self, queries: [str]):
        if queries:
            self.__queries = queries

    def setAutoscalers(self, autoscalers: [str]):
        if autoscalers:
            self.__autoscalers = autoscalers

    def setMetrics(self, metrics: [str]):
        if metrics:
            self.__metrics = metrics

    def getMetrics(self):
        return self.__metrics

    # Shared folder structures
    def __getDataFolder(self, main_folder: str):
        return f"{main_folder}/full-data"

    def __getGraphFolder(self, main_folder: str, include_graph_folder=True):
        if include_graph_folder:
            return f"{main_folder}/graphs"
        else:
            return f"{main_folder}"

    def getExperiments(self, data_label: str):
        return Experiment.getAllExperiments(self.__queries, self.__autoscalers, label=data_label)


    # Naming functionality
    @staticmethod
    def getNamingPrefix(prefix: str):
        return "" if prefix == "" else f"{prefix}_"

    @staticmethod
    def getNamingPostfix(postfix: str):
        return "" if postfix == "" else f"_{postfix}"

    # ArgParse
    def includeArgumentsInParser(self, argumentParser: argparse.ArgumentParser):

        def includeMetricsInParser(parser: argparse.ArgumentParser):
            parser.add_argument('--metrics', nargs='*', type=str)

        def includeQueriesInParser(parser: argparse.ArgumentParser):
            parser.add_argument('--queries', nargs='*', type=str)

        def includeAutoscalersInParser(parser: argparse.ArgumentParser):
            parser.add_argument('--autoscalers', nargs='*', type=str)

        includeMetricsInParser(argumentParser)
        includeQueriesInParser(argumentParser)
        includeAutoscalersInParser(argumentParser)

    def fetchArgumentsFromNamespace(self, namespace: argparse.Namespace):
        def fetchMetricsFromNamespace(args: argparse.Namespace):
            if args.metrics:
                metrics = []
                invalid_metrics = []
                for arg in args.metrics:
                    if Metrics.isMetricClass(arg):
                        metrics.append(arg)
                    else:
                        invalid_metrics.append(arg)
                if invalid_metrics:
                    print(f"The following provided metrics are invalid: {invalid_metrics}")
                    print(f"Use any of the following available metrics: {Metrics.getAllMetricClasses()}")
                self.setMetrics(metrics)

        def fetchQueriesFromNamespace(args: argparse.Namespace):
            if args.queries:
                queries = []
                invalid_queries = []
                for arg in args.queries:
                    if Queries.isQuery(arg):
                        queries.append(arg)
                    else:
                        invalid_queries.append(arg)
                if invalid_queries:
                    print(f"The following provided metrics are invalid: {invalid_queries}")
                    print(f"Use any of the following available metrics: {Queries.getAllQueries()}")
                self.setQueries(queries)

        def fetchAutoscalersFromNamespace(args: argparse.Namespace):
            if args.autoscalers:
                autoscalers = []
                invalid_autoscalers = []
                for arg in args.autoscalers:
                    if Autoscalers.isAutoscaler(arg):
                        autoscalers.append(arg)
                    else:
                        invalid_autoscalers.append(arg)
                if invalid_autoscalers:
                    print(f"The following provided metrics are invalid: {invalid_autoscalers}")
                    print(f"Use any of the following available metrics: {Autoscalers.getAllAutoscalers()}")
                self.setAutoscalers(autoscalers)

        fetchMetricsFromNamespace(namespace)
        fetchQueriesFromNamespace(namespace)
        fetchAutoscalersFromNamespace(namespace)


class SingleFolderPlotParameters(PlotParameters):
    # Required
    __main_folder: "ERROR: No main folder set"
    __data_label: "ERROR: No data prefix set"
    __result_folder_name: str
    __result_label = ""

    def __init__(self, default_result_folder_name: str):
        self.__result_folder = default_result_folder_name

    def setMainFolder(self, main_folder: str):
        if main_folder:
            self.__main_folder = main_folder

    def setDataLabel(self, data_label: str):
        if data_label:
            self.__data_label = data_label

    # Overwrite parent folders to make fetching the datafolder easier
    def getDataFolder(self):
        return self.__getDataFolder(self.__main_folder)

    def getDataLabel(self):
        return self.__data_label

    # Overwrite parent folders to make fetching the datafolder easier
    def getGraphFolder(self):
        return self.getGraphFolder(self.__main_folder)

    # Set a custom result folder name
    def setCustomResultFolderName(self, result_folder_name: str):
        if result_folder_name:
            self.__result_folder_name = result_folder_name

    # Get ResultFolder to save the results
    def getResultFolder(self):
        return f"{self.getGraphFolder()/self.__result_folder_name}"

    # Set a label for the result file
    def setResultLabel(self, resultLabel: str):
        if resultLabel:
            self.__result_label = resultLabel

    def getExperimentFiles(self):
        return ExperimentFile.getAvailableExperimentFiles(self.getDataFolder(), super().__getExperiments(self.getDataLabel()))

    # Get the result label of a file
    def getResultLabel(self):
        return self.__result_label

    def __getResultFileName(self, experimentFile: ExperimentFile, postFix=""):
        prefix = self.getNamingPrefix(self.getResultLabel())
        postfix = self.getNamingPostfix(postFix)
        experimentName = experimentFile.getExperimentName()
        return f"{prefix}{experimentName}{postfix}"

    def includeArgumentsInParser(self, argumentParser: argparse.ArgumentParser):
        super().includeArgumentsInParser(argumentParser)

        def includeMainFolderInParser(parser: argparse.ArgumentParser):
            parser.add_argument('source_directory', type=str,
                                help="Directory in which datafiles can be found at src_dir/full-data")

        def includeSourceLabelInParser(parser: argparse.ArgumentParser):
            parser.add_argument('source_label', type=str)

        def includeResultFolderInParser(parser: argparse.ArgumentParser):
            parser.add_argument('-result_folder_name', type=str, nargs="?")

        def includeResultLabelInParser(parser: argparse.ArgumentParser):
            parser.add_argument('-result_label', type=str, nargs="?")

        includeMainFolderInParser(argumentParser)
        includeSourceLabelInParser(argumentParser)
        includeResultFolderInParser(argumentParser)
        includeResultLabelInParser(argumentParser)


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

        fetchMainFolderFromNamespace(namespace)
        fetchSourceLabelFromNamespace(namespace)
        fetchResultFolderFromNamespace(namespace)
        fetchResultLabelFromNamespace(namespace)


class IndividualParameters(SingleFolderPlotParameters):
    __plot_thresholds = False

    def __init__(self):
        default_result_folder_name = "individual-graph"
        super().__init__(default_result_folder_name)

    # Result file naming
    def getResultFileName(self, experimentFile: ExperimentFile):
        postfix = "_thresholds" if self.__plot_thresholds else ""
        return self.__getResultFileName(experimentFile, postfix = postfix)

    # Also plot result threshold
    def setPlotThreshold(self, plot_thresholds: bool):
        if plot_thresholds:
            self.__plot_thresholds = plot_thresholds

    def getPlotThresholds(self):
        return self.__plot_thresholds

    def includeArgumentsInParser(self, argumentParser: argparse.ArgumentParser):
        super().includeArgumentsInParser(argumentParser)

        def includePlotThresholds(parser: argparse.ArgumentParser):
            parser.add_argument('--plot_thresholds', action='store_true')
        includePlotThresholds(argumentParser)

    def fetchArgumentsFromNamespace(self, namespace: argparse.Namespace):
        super().fetchArgumentsFromNamespace(namespace)

        def fetchPlotThresholds(args: argparse.Namespace):
            self.setPlotThreshold(args.plot_thresholds)

        fetchPlotThresholds(namespace)


def plotIndividualExperiments(parameters: IndividualParameters):
    experimentFiles = parameters.getExperimentFiles()
    for experimentFile in experimentFiles:
        plotDataFile(
            file=experimentFile,
            saveDirectory=parameters.getResultFolder(),
            saveName=parameters.getResultFileName(experimentFile),
            metrics=parameters.getMetrics(),
            plotThresholds=parameters.getPlotThresholds()
         )


def parseArguments():
    parameters = IndividualParameters()

    # Parse arguments
    parser = argparse.ArgumentParser(description='Plot individual experiments')
    parameters.includeArgumentsInParser(parser)

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetchArgumentsFromNamespace(namespace)

    # Call plot function
    plotIndividualExperiments(parameters)


if __name__ == "__main__":
    parseArguments()
