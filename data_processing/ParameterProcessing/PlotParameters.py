import argparse
from typing import Tuple

from .StaticPlotFunctions import StaticPlotFunctions
from DataClasses import Queries, Autoscalers, Metrics, Experiment


class PlotParameters(StaticPlotFunctions):
    # Overall queries, autoscalers, metrics
    __queries = Queries.getAllQueries()
    __autoscalers = Autoscalers.getAllAutoscalers()
    __metrics = Metrics.getAllMetricClasses()

    # Metric limits
    __metric_ranges: [Tuple[str, float, float]] = []

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

    def setMetricRanges(self, metric_ranges: [Tuple[str, float, float]]):
        self.__metric_ranges = metric_ranges

    def getMetricRanges(self):
        return self.__metric_ranges

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

        def includeMetricRangesInParser(parser: argparse.ArgumentParser):
            parser.add_argument('--metric_range', nargs=3, action='append')


        includeMetricsInParser(argumentParser)
        includeQueriesInParser(argumentParser)
        includeAutoscalersInParser(argumentParser)
        includeMetricRangesInParser(argumentParser)

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

        def fetchMetricRanges(args: argparse.Namespace):
            if args.metric_range:
                ranges = []
                for limit in args.metric_range:
                    metric = limit[0]
                    min_val = limit[1]
                    max_val = limit[2]

                    if not Metrics.isMetricClass(metric):
                        print(f"Error: metric {metric} is not a valid metric. Ignoring provided metric-limit")
                        print(f"Use any of the following available metrics: {Metrics.getAllMetricClasses()}")
                        continue
                    try:
                        min_val = float(min_val)
                        max_val = float(max_val)
                    except ValueError:
                        print(f"Error: {min_val} and {max_val} should be of type float. Ignoring provided metric-limit")
                        continue

                    if max_val <= min_val:
                        print(f"Error: {min_val} is not smaller than {max_val}. Ignoring provided metric-limit")
                        continue
                    ranges.append((metric, min_val, max_val))
                self.setMetricRanges(ranges)

        fetchMetricsFromNamespace(namespace)
        fetchQueriesFromNamespace(namespace)
        fetchAutoscalersFromNamespace(namespace)
        fetchMetricRanges(namespace)

