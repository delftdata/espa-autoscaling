import argparse

from DataClasses import Queries, Autoscalers, Metrics, Modes


class PlotParameters():
    # Queries, autoscalers, metrics, tags
    __queries = Queries.get_all_queries()
    __autoscalers = Autoscalers.get_all_autoscalers()
    __modes = Modes.get_all_modes()
    __tags = []

    # Metric limits
    __metrics = Metrics.get_all_metric_classes()
    # __metric_ranges: {str, (float, float)} = Metrics.metric_range_mapping
    # __option_metric_ranges = True
    #
    # def __init__(self, option_metric_ranges=True):
    #     self.__option_metric_ranges = option_metric_ranges

    # Queries getter and setter
    def set_queries(self, queries: [str]):
        if queries:
            self.__queries = queries

    def get_queries(self) -> [str]:
        return self.__queries

    # Autoscalers getter and setter
    def set_autoscalers(self, autoscalers: [str]):
        if autoscalers:
            self.__autoscalers = autoscalers

    def get_autoscalers(self) -> [str]:
        return self.__autoscalers

    # Modes getter and setter
    def set_modes(self, modes: [str]):
        if modes:
            self.__modes = modes

    def get_modes(self) -> str:
        return self.__modes

    # Tags getter and setter
    def set_tags(self, tags: [str]):
        self.__tags = tags

    def get_tags(self) -> str:
        return self.__tags

    # Metrics getter and setter
    def get_metrics(self) -> [str]:
        return self.__metrics

    def set_metrics(self, metrics: [str]):
        if metrics:
            self.__metrics = metrics

    # Get and set metric ranges
    # def setMetricRanges(self, metric_ranges: {str, (float, float)}):
    #     self.__metric_ranges = metric_ranges
    #
    # def getMetricRanges(self):
    #     return self.__metric_ranges

    def include_arguments_in_parser(self, argument_parser: argparse.ArgumentParser):

        def include_metrics_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('--metrics', nargs='*', type=str)

        def include_queries_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('--queries', nargs='*', type=str)

        def include_autoscalers_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('--autoscalers', nargs='*', type=str)

        def include_modes_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('--modes', nargs='*', type=str)

        def include_tags_in_parser(parser: argparse.ArgumentParser):
            parser.add_argument('--tags', nargs='*', type=str)

        # def includeMetricRangesInParser(parser: argparse.ArgumentParser):
        #     parser.add_argument('--metric_range', nargs=3, action='append')

        include_metrics_in_parser(argument_parser)
        include_queries_in_parser(argument_parser)
        include_autoscalers_in_parser(argument_parser)
        include_modes_in_parser(argument_parser)
        include_tags_in_parser(argument_parser)

        # if self.__option_metric_ranges:
        #     includeMetricRangesInParser(argumentParser)

    def fetch_arguments_from_namespace(self, namespace: argparse.Namespace):

        def filter_out_unsupported_arguments(provided_arguments, all_supported_arguments: [], arg_name="undefined"):
            supported_args = []
            invalid_args = []
            for argument in provided_arguments:
                if argument in all_supported_arguments:
                    supported_args.append(argument)
                else:
                    invalid_args.append(argument)
            if invalid_args:
                print(f"The following provided arguments of '{arg_name}' are invalid: {invalid_args}")
                print(f"Use any of the following available arguments: {all_supported_arguments}")
            return supported_args


        def fetch_autoscalers_from_namespace(args: argparse.Namespace):
            all_autoscalers = Autoscalers.get_all_autoscalers()
            if args.autoscalers:
                provided_autoscalers = args.autoscalers
                autoscalers = filter_out_unsupported_arguments(provided_autoscalers, all_autoscalers, "autoscalers")
                self.set_autoscalers(autoscalers)

        def fetch_queries_from_namespace(args: argparse.Namespace):
            all_queries = Queries.get_all_queries()
            if args.queries:
                provided_queries = args.queries
                queries = filter_out_unsupported_arguments(provided_queries, all_queries, "queries")
                self.set_queries(queries)

        def fetch_modes_from_namespace(args: argparse.Namespace):
            all_modes = Modes.get_all_modes()
            if args.modes:
                provided_modes = args.modes
                modes = filter_out_unsupported_arguments(provided_modes, all_modes, "modes")
                self.set_modes(modes)

        def fetch_tags_from_namespace(args: argparse.Namespace):
            if args.tags:
                provided_tags = args.tags
                self.set_tags(provided_tags)

        def fetch_metrics_from_namespace(args: argparse.Namespace):
            all_metric_classes = Metrics.get_all_metric_classes()
            if args.metrics:
                provided_metric_classes = args.metrics
                metric_classes = filter_out_unsupported_arguments(provided_metric_classes, all_metric_classes,
                                                                  "metrics")
                self.set_metrics(metric_classes)

        # def fetchMetricRanges(args: argparse.Namespace):
        #     if args.metric_range:
        #         ranges = []
        #         for limit in args.metric_range:
        #             metric = limit[0]
        #             min_val = limit[1]
        #             max_val = limit[2]
        #
        #             if not Metrics.isMetricClass(metric):
        #                 print(f"Error: metric {metric} is not a valid metric. Ignoring provided metric-limit")
        #                 print(f"Use any of the following available metrics: {Metrics.getAllMetricClasses()}")
        #                 continue
        #             try:
        #                 min_val = float(min_val)
        #                 max_val = float(max_val)
        #             except ValueError:
        #                 print(f"Error: {min_val} and {max_val} should be of type float. Ignoring provided metric-limit")
        #                 continue
        #
        #             if max_val <= min_val:
        #                 print(f"Error: {min_val} is not smaller than {max_val}. Ignoring provided metric-limit")
        #                 continue
        #             ranges.append((metric, min_val, max_val))
        #         self.setMetricRanges(ranges)

        fetch_autoscalers_from_namespace(namespace)
        fetch_queries_from_namespace(namespace)
        fetch_modes_from_namespace(namespace)
        fetch_tags_from_namespace(namespace)
        fetch_metrics_from_namespace(namespace)
        # if self.__option_metric_ranges:
        #     fetchMetricRanges(namespace)

