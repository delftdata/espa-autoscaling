from .Experiment import Experiment
import os
import os.path

class ExperimentFile:
    experiment: Experiment
    directory: str
    datafile = "FILE NOT FOUND"
    print: str

    def getFilePath(self, directory: str, experiment: Experiment):
        filename = f"{experiment.getExperimentName()}_data.csv"
        path = f"{directory}/{filename}"
        print(path)
        return path

    def __init__(self, directory: str, experiment: Experiment, printingEnabled=True):
        self.printingEnabled=printingEnabled
        self.experiment = experiment
        if os.path.isdir(directory):
            self.directory = directory
            filepath = self.getFilePath(
                self.directory,
                self.experiment
            )

            if os.path.isfile(filepath):
                self.datafile = filepath
            elif self.printingEnabled:
                print(f"Error: {filepath} does not exist. Could not initialize ExperimentFile of {experiment}")
        elif self.printingEnabled:
            print(f"Error: {directory} does not exist. Could not initialize ExperimentFile of {experiment}")

    def __str__(self):
        return f"ExperimentFile[{self.datafile}, {self.experiment}]"

    __repr__ = __str__

    def fileExists(self) -> bool:
        return os.path.isfile(self.datafile)

    def getExperiment(self):
        return self.experiment

    def getAutoscaler(self):
        return self.getExperiment().autoscaler

    def getQuery(self):
        return self.getExperiment().query

    def getVariable(self):
        return self.getExperiment().variable

    def getLabel(self):
        return self.getExperiment().label

    def getExperimentName(self):
        return self.getExperiment().getExperimentName()

    @staticmethod
    def _getExperimentFileFromExperiment(directory: str, experiment: Experiment, printingEnabled=True):
        return ExperimentFile(directory, experiment, printingEnabled=printingEnabled)

    @staticmethod
    def _getExperimentFileFromInfo(directory: str, query: str, autoscaler: str, variable: str, label="",
                                   printingEnabled=True):
        experiment = Experiment.getExperiment(query, autoscaler, variable, label=label)
        return ExperimentFile._getExperimentFileFromExperiment(directory, experiment, printingEnabled=printingEnabled)

    @staticmethod
    def getAvailableExperimentFiles(directory: str, experiments: [Experiment], printingEnabled=True):
        """
        Get the ExperimentFiles corresponding to the ones provided as experiments.
        If no corresponding file can be found, this one is left out of the output.
        :param directory: Directory containing the available files
        :param experiments: Experiments to fetch the corresponding files from
        :param printingEnabled: Print errormessages signaling absent files
        :return: A list of available experiment files.
        """
        experimentFiles = []
        for experiment in experiments:
            experimentFile = ExperimentFile._getExperimentFileFromExperiment(directory, experiment,
                                                                             printingEnabled=printingEnabled)
            if experimentFile.fileExists():
                experimentFiles.append(experimentFile)
        return experimentFiles

    @staticmethod
    def getAllAvailableExperimentFiles(directory: str, label="", printingEnabled=True):
        """
        Get All available ExperimentFiles from the provided directory.
        Experiment configurations to look for are generated from information provided by the Autoscaler and Query class
        :param directory: Directory to fetch all available ExperimentFiles from
        :param printingEnabled: Print error messages.
        :return:
        """
        experiments = Experiment.getAllExperiments(label=label)
        return ExperimentFile.getAvailableExperimentFiles(directory, experiments, printingEnabled=printingEnabled)
