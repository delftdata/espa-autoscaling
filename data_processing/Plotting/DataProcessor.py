from DataClasses import ExperimentFile
import pandas as pd


def get_data_frame(experiment_file: ExperimentFile):
    return pd.read_csv(experiment_file.file_path)


def get_time_column_from_data_frame(data_frame):
    time_column = data_frame["minutes"]
    return time_column


# Data processing
def getMetricColumn(metric, data):
    if metric in data:
        return data[metric]
    else:
        print(f"Warning: metric {metric} not found")
        return None


def filter_out_missing_metric_names(metric_names, data, print_missing_metrics=False):
    existing_metric_names = []
    for metric_name in metric_names:
        if metric_name in data:
            existing_metric_names.append(metric_name)
        elif print_missing_metrics:
            print(f"Warning: metric {metric_name} is not present in the provided data.")
    return existing_metric_names


def interpolate_data_column(data_column):
    # Interpolate and fill NaN with 0
    data_column = data_column.interpolate()
    data_column = data_column.fillna(0)
    return data_column


# Calculate metrics
def getAverageMetricFromData(data, metricName):
    metric_column = data[metricName]
    return sum(metric_column) / len(metric_column)


def getAverageMetric(experimentFile: ExperimentFile, metricName: str):
    data = pd.read_csv(experimentFile.file_path)
    return getAverageMetricFromData(data, metricName)


def getAverageMetrics(experimentFile: ExperimentFile, metrics):
    data = pd.read_csv(experimentFile.file_path)
    results = []
    for metric in metrics:
        results.append(getAverageMetricFromData(data, metric))
    return results


def getTotalRescalingActions(experimentFile: ExperimentFile):
    data = pd.read_csv(experimentFile.file_path)
    taskmanagers = data['taskmanager'].tolist()
    previous_number_taskmanagers = taskmanagers[0]
    scaling_events = 0
    for val in taskmanagers:
        if val != previous_number_taskmanagers:
            scaling_events += 1
        previous_number_taskmanagers = val
    return scaling_events
