import argparse

from ParameterProcessing import SingleFolderPlotParameters, StaticPlotFunctions
from DataClasses import Experiment, ExperimentFile
from Plotting import overlapAndPlotMultipleDataFiles


def plotAutoscalerConfigurations(parameters: SingleFolderPlotParameters):
    def getSaveName(queryName: str, autoscalerName: str):
        prefixName = parameters.getResultLabel()
        postFixName = "thresholds" if parameters.getPlotThresholds() else ""

        prefix = StaticPlotFunctions.getNamingPrefix(prefixName)
        postfix = StaticPlotFunctions.getNamingPostfix(postFixName)
        return f"{prefix}q{queryName}_{autoscalerName}{postfix}"

    for query in parameters.getQueries():
        for autoscaler in parameters.getAutoscalers():
            experiments = Experiment.getAllExperiments(query, autoscaler, label=parameters.getDataLabel())
            experimentFiles = ExperimentFile.getAvailableExperimentFiles(parameters.getDataFolder(), experiments)
            if len(experimentFiles) > 0:
                overlapAndPlotMultipleDataFiles(
                    files=experimentFiles,
                    saveDirectory=parameters.getResultFolder(),
                    saveName=getSaveName(query, autoscaler),
                    metric_ranges=parameters.getMetricRanges(),
                    plotThresholds=parameters.getPlotThresholds(),
                    metrics=parameters.getMetrics(),
                )



def parseArguments():
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("autoscaler-variables-combined")

    # Parse arguments
    parser = argparse.ArgumentParser(description='Compare autoscaler comparisons')
    parameters.includeArgumentsInParser(parser)

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetchArgumentsFromNamespace(namespace)

    # Call plot function
    plotAutoscalerConfigurations(parameters)


if __name__ == "__main__":
    parseArguments()