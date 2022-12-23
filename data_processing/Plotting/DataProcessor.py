from DataClasses import ExperimentFile
import pandas as pd
import numpy as np


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


def get_experiment_dataframe_mapping(experiment_files: [ExperimentFile]):
    experiment_dataframe_mapping = {}
    for experiment_file in experiment_files:
        data_frame = get_data_frame(experiment_file)
        experiment_dataframe_mapping[experiment_file] = data_frame
    return experiment_dataframe_mapping


def get_shared_metrics_from_dataframes(metric_names: [str], dataframes):
    for dataframe in dataframes:
        metric_names = filter_out_missing_metric_names(metric_names, dataframe)
    return metric_names




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
def __get_average_metric_from_dataframe(data_frame, metric_name):
    metric_column = getMetricColumn(metric_name, data_frame)
    metric_column = metric_column[~np.isnan(metric_column)]
    return sum(metric_column) / len(metric_column)


def get_average_metrics_from_dataframe(data_frame, metric_names: [str]):
    metric_names = filter_out_missing_metric_names(metric_names, data_frame)
    results = []
    for metric in metric_names:
        results.append(__get_average_metric_from_dataframe(data_frame, metric))
    return results


# Calculate metrics
def __get_maximum_metric_from_dataframe(data_frame, metric_name):
    metric_column = getMetricColumn(metric_name, data_frame)
    metric_column = metric_column[~np.isnan(metric_column)]
    return max(metric_column)


def get_maximum_metrics_from_dataframe(data_frame, metric_names: [str]):
    metric_names = filter_out_missing_metric_names(metric_names, data_frame)
    results = []
    for metric in metric_names:
        results.append(__get_maximum_metric_from_dataframe(data_frame, metric))
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
