import os.path

class Metrics:
    """
    Helper class containing all available metrics used by the experiments
    """
    INPUT_RATE = "input_rate"
    TASKMANAGER = "taskmanager"
    LATENCY = "latency"
    LAG = "lag"
    THROUGHPUT = "throughput"
    CPU_LOAD = "CPU_load"
    BACKPRESSURE = "backpressure"
    BUSY_TIME = "busy_time"
    IDLE_TIME = "idle_time"

    @staticmethod
    def getAllMetricClasses():
        """
        Get a list of all MetricClasses
        :return: list of all MetricClasses
        """
        return [
            Metrics.INPUT_RATE,
            Metrics.TASKMANAGER,
            Metrics.LATENCY,
            Metrics.LAG,
            Metrics.THROUGHPUT,
            Metrics.CPU_LOAD,
            Metrics.BACKPRESSURE,
            Metrics.BUSY_TIME,
            Metrics.IDLE_TIME
        ]

    @staticmethod
    def isMetricClass(metric: str):
        return Metrics.getAllMetricClasses().__contains__(metric)


class Autoscalers:
    """
    Helperclass containing all possible autoscalers with their corresponding variables used by the experiments.
    """
    DHALION = "dhalion"
    DHALION_VARIABLES = ["1", "5", "10"]
    DS2_ORIGINAL = "ds2-original"
    DS2_ORIGINAL_VARIABLES = ["0", "33", "66"]
    DS2_UPDATED = "ds2-updated"
    DS2_UPDATED_VARIABLES = ["0", "33", "66"]
    HPA = "HPA"
    HPA_VARIABLES = ["50", "70", "90"]
    VARGA1 = "varga1"
    VARGA1_VARIABLES = ["0.3", "0.5", "0.7"]
    VARGA2 = "varga2"
    VARGA2_VARIABLES = ["0.3", "0.5", "0.7"]

    @staticmethod
    def getVariablesOfAutoscaler(autoscaler) -> [str]:
        if autoscaler == Autoscalers.DHALION:
            return Autoscalers.DHALION_VARIABLES
        elif autoscaler == Autoscalers.DS2_ORIGINAL:
            return Autoscalers.DS2_ORIGINAL_VARIABLES
        elif autoscaler == Autoscalers.DS2_UPDATED:
            return Autoscalers.DS2_UPDATED_VARIABLES
        elif autoscaler == Autoscalers.HPA:
            return Autoscalers.HPA_VARIABLES
        elif autoscaler == Autoscalers.VARGA1:
            return Autoscalers.VARGA1_VARIABLES
        elif autoscaler == Autoscalers.VARGA2:
            return Autoscalers.VARGA2_VARIABLES
        else:
            print(f"Error: did not find variables belonging to {autoscaler}.")
            return []

    @staticmethod
    def getAllAutoscalers() -> [str]:
        return [
            Autoscalers.DHALION,
            Autoscalers.DS2_ORIGINAL,
            Autoscalers.DS2_UPDATED,
            Autoscalers.HPA,
            Autoscalers.VARGA1,
            Autoscalers.VARGA2
        ]

    @staticmethod
    def getAllAutoscalerVariables() -> [str]:
        return list(map(lambda autoscaler: Autoscalers.getVariablesOfAutoscaler(autoscaler),
                        Autoscalers.getAllAutoscalers()))

    @staticmethod
    def getAutoscalerAndVariables() -> [(str, [str])]:
        return list(zip(Autoscalers.getAllAutoscalers(), Autoscalers.getAllAutoscalerVariables()))

    @staticmethod
    def isAutoscaler(autoscaler) -> bool:
        return Autoscalers.getAllAutoscalers().__contains__(autoscaler)


class Queries:
    """
    Helperclass containing all possible autoscalers used by the experiments.
    """
    QUERY_1 = "1"
    QUERY_3 = "3"
    QUERY_11 = "11"

    @staticmethod
    def getAllQueries() -> [str]:
        return [
            Queries.QUERY_1,
            Queries.QUERY_3,
            Queries.QUERY_11
        ]

    @staticmethod
    def isQuery(query) -> bool:
        return Queries.getAllQueries().__contains__(query)


class Experiment:
    query: str
    autoscaler: str
    variable: str
    label: str

    def __init__(self, query: str, autoscaler: str, variable: str, label=""):
        """
        Constructor of an experiment class.
        This class represents an experiment and requires the following parameters:
        :param query: query to process (must be part of Query class)
        :param autoscaler: autoscaler used in expeirment (must be part of Autoscaler class)
        :param variable: variable used as configuration setting for the autoscaler (must also a valid variable as found
        in the Autoscaler class)
        :param label: Optional free-form label can be used to describe additional experiment configurations.
        """
        self.query = query
        self.autoscaler = autoscaler
        self.variable = variable
        self.label = label
        if not self.isValidExperiment():
            print(f"Error constructing experiment: {self} is not a valid experiment!")

    def __str__(self):
        if (self.label == ""):
            return f"Experiment[{self.query}, {self.autoscaler}-{self.variable}]"
        else:
            return f"Experiment[({self.label}) {self.query}, {self.autoscaler}-{self.variable}]"

    __repr__ = __str__

    def isValidExperiment(self) -> bool:
        return (
                Queries.isQuery(self.query) and
                Autoscalers.isAutoscaler(self.autoscaler) and
                Autoscalers.getVariablesOfAutoscaler(self.autoscaler).__contains__(self.variable)
        )

    def isSimilarExperiment(self, other, ignoreLabel=False):
        if type(other) == Experiment:
            isSimilar = True
            isSimilar = isSimilar and self.query == other.query
            isSimilar = isSimilar and self.autoscaler == other.autoscaler
            isSimilar = isSimilar and self.variable == other.variable
            isSimilar = isSimilar and (ignoreLabel or self.label == other.label)
            return isSimilar
        return False

    def getExperimentName(self):
        name = f"q{self.query}_{self.autoscaler}_{self.variable}"
        if self.label != "":
            name = f"{self.label}_{name}"
        return name

    @staticmethod
    def getExperiment(query: str, autoscaler: str, variable: str, label=""):
        return Experiment(query, autoscaler, variable, label=label)

    @staticmethod
    def getAllExperiments(queries=None, autoscalers=None, label=""):
        if queries is None:
            queries = Queries.getAllQueries()
        elif not isinstance(queries, list):
            queries = [str(queries)]

        if autoscalers is None:
            autoscalers = Autoscalers.getAllAutoscalers()
        elif type(autoscalers) == str:
            autoscalers = [autoscalers]

        experiments = []
        for query in queries:
            for autoscaler in autoscalers:
                for var in Autoscalers.getVariablesOfAutoscaler(autoscaler):
                    experiments.append(Experiment.getExperiment(query, autoscaler, var, label=label))
        return experiments


class ExperimentFile:
    experiment: Experiment
    directory: str
    datafile = "FILE NOT FOUND"
    print: str

    def getFilePath(self, directory, query, autoscaler, variable, label):
        filename = f"q{query}_{autoscaler}_{variable}.csv"
        if label != "":
            filename = f"{label}_{filename}"
        return f"{directory}/{filename}"

    def __init__(self, directory: str, experiment: Experiment, printingEnabled=True):
        self.printingEnabled=printingEnabled
        self.experiment = experiment
        if os.path.isdir(directory):
            self.directory = directory
            filepath = self.getFilePath(
                self.directory,
                self.experiment.query,
                self.experiment.autoscaler,
                self.experiment.variable,
                self.experiment.label
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


