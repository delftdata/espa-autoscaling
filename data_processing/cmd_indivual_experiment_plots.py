import argparse

from DataClasses import Autoscalers, Metrics
from Plotting import plotDataFile
from ParameterProcessing import SingleFolderPlotParameters, StaticPlotFunctions


def plotIndividualExperiments(parameters: SingleFolderPlotParameters):
    def getSaveName():
        prefixName = parameters.getResultLabel()
        postFixName = "thresholds" if parameters.getPlotThresholds() else ""

        prefix = StaticPlotFunctions.getNamingPrefix(prefixName)
        postfix = StaticPlotFunctions.getNamingPostfix(postFixName)
        experimentName = experimentFile.getExperimentName()
        return f"{prefix}{experimentName}{postfix}"

    experimentFiles = parameters.getExperimentFiles()
    for experimentFile in experimentFiles:

        if parameters.getMetrics() == Metrics.getDefaultMetricClasses():
            parameters.setMetrics(Metrics.getAllMetricClassesForAutoscaler(experimentFile.getAutoscaler()))

        plotDataFile(
            file=experimentFile,
            saveDirectory=parameters.getResultFolder(),
            saveName=getSaveName(),
            metrics=parameters.getMetrics(),
            metric_ranges=parameters.getMetricRanges(),
            plotThresholds=parameters.getPlotThresholds(),
        )


def parseArguments():
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("individual-plots")

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
