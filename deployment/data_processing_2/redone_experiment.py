from helperclasses import Experiment, ExperimentFile, Queries, Autoscalers, Metrics

def plotRedoneExperiment():
    DATA_FOLDER_REDONE = "./results/redone"
    RESULT_FOLDER = "./results/plots"

    queries = [
        Queries.QUERY_1,
        # Queries.QUERY_3,
        # Queries.QUERY_11
    ]
    autoscaler = [
        Autoscalers.DHALION,
        # Autoscalers.DS2_ORIGINAL,
        # Autoscalers.DS2_UPDATED,
        # Autoscalers.HPA,
        # Autoscalers.VARGA1,
        # Autoscalers.VARGA2,
    ]
    metrics = [
        Metrics.INPUT_RATE,
        Metrics.TASKMANAGER,
        Metrics.LATENCY,
        Metrics.LAG,
        Metrics.THROUGHPUT,
        Metrics.CPU_LOAD,
        Metrics.BACKPRESSURE,
        Metrics.BUSY_TIME,
        Metrics.IDLE_TIME,
    ]
    # experiments = Experiment.getAllExperiments(queries, autoscaler, label="test")
    # experimentFiles = ExperimentFile.getAvailableExperimentFiles(DATA_FOLDER, experiments)
    # overlapAndPlotMultipleDataFiles(ExperimentFile.getAllAvailableExperimentFiles(DATA_FOLDER), metrics=metrics)


if __name__ == "__main__":
    plotRedoneExperiment()