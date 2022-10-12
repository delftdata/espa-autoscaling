from src.helperclasses import Metrics, Autoscalers, Queries

def getDataFolder(folder):
    return f"{folder}/full-data"


def getGraphFolder(folder, create_graph_folder=True):
    if create_graph_folder:
        return f"{folder}/graphs"
    else:
        return f"{folder}"

def includeMetrics(parser):
    parser.add_argument('--metrics', nargs='*', type=str)


def getMetrics(args):
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
        return metrics
    else:
        return Metrics.getAllMetricClasses()


def includeAutoscalers(parser):
    parser.add_argument('--autoscalers', nargs='*', type=str)

def getAutoscalers(args):
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
        return autoscalers
    else:
        return Autoscalers.getAllAutoscalers()


def includeQueries(parser):
    parser.add_argument('--queries', nargs='*', type=str)


def getQueries(args):
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
        return queries
    else:
        return Queries.getAllQueries()

