import argparse

from .StaticPlotFunctions import StaticPlotFunctions
from DataClasses import Queries, Autoscalers, Metrics, Experiment


class PlotParameters(StaticPlotFunctions):
    # Overall queries, autoscalers, metrics
    __queries = Queries.getAllQueries()
    __autoscalers = Autoscalers.getAllAutoscalers()
    __metrics = Metrics.getAllMetricClasses()

    def setQueries(self, queries: [str]):
        if queries:
            self.__queries = queries

    def getQueries(self):
        return self.__queries

    def setAutoscalers(self, autoscalers: [str]):
        if autoscalers:
            self.__autoscalers = autoscalers

    def getAutoscalers(self):
        return self.__autoscalers

    def getMetrics(self):
        return self.__metrics

    def setMetrics(self, metrics: [str]):
        if metrics:
            self.__metrics = metrics



    def getExperimentsWithDatalabel(self, data_label: str):
        return Experiment.getAllExperiments(self.__queries, self.__autoscalers, label=data_label)

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

