import argparse
from typing import Tuple

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


        plotDataFile(
            file=experimentFile,
            saveDirectory=parameters.getResultFolder(),
            saveName=getSaveName(),
            metrics=parameters.getMetrics(),
            plotThresholds=parameters.getPlotThresholds()
        )


def parseArguments():
    parameters: SingleFolderPlotParameters = SingleFolderPlotParameters("individual-plots")

    # Parse arguments
    parser = argparse.ArgumentParser(description='Plot individual experiments')
    parameters.includeArgumentsInParser(parser)
    parser.add_argument('--metric_limit', nargs=3, action='append')

    # Fetch results from arguments
    namespace = parser.parse_args()
    parameters.fetchArgumentsFromNamespace(namespace)
    print(namespace.metric_limit)

    # Call plot function
    # plotIndividualExperiments(parameters)


if __name__ == "__main__":
    parseArguments()
