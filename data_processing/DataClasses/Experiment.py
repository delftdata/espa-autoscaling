from .Autoscalers import Autoscalers
from .Queries import Queries


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
       return f"Experiment[{self.getExperimentName()}]"

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
        name = f"q{self.query}_{self.autoscaler}"
        if self.variable:
            name = f"{name}_{self.variable}"
        if self.label:
            name = f"[{self.label}]{name}"
        tag = "[c5m]"
        name = f"{tag}{name}"
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
