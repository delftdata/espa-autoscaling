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


def get_maximum_metrics_from_dataframe(data_frame, metric_names: [str]) -> [float]:
    """
    Get the maximum of the provided metrics of the data in the provided data_frame
    :param data_frame: Data_frame containing metric data to calculate maximum from.
    :param metric_names: Column names representing the metrics the maximum should be calculated from.
    :return: A list of maximum metrics of the provided data_frame
    """
    metric_names = filter_out_missing_metric_names(metric_names, data_frame)
    results = []
    for metric_name in metric_names:
        metric_column = getMetricColumn(metric_name, data_frame)
        metric_column = metric_column[~np.isnan(metric_column)]
        max_result = max(metric_column)
        results.append(max_result)
    return results


def get_average_metrics_from_dataframe(data_frame, metric_names: [str]) -> [float]:
    """
    Get the average of the provided metrics of the data in the provided data_frame
    :param data_frame: Data_frame containing metric data to calculate average from.
    :param metric_names: Column names representing the metrics the average should be calculated from.
    :return: A list of average metrics of the provided data_frame
    """
    metric_names = filter_out_missing_metric_names(metric_names, data_frame)
    results = []
    for metric_name in metric_names:
        metric_column = getMetricColumn(metric_name, data_frame)
        metric_column = metric_column[~np.isnan(metric_column)]
        avg_result = sum(metric_column) / len(metric_column)
        results.append(avg_result)
    return results


def get_percentile_metrics_from_dataframe(data_frame, metric_names: [str], percentile: int) -> [float]:
    """
    Get the percentile of the provided metrics of the data in the provided data_frame
    :param data_frame: Data_frame containing metric data to calculate percentile from.
    :param metric_names: Column names representing the metrics the percentile should be calculated from.
    :param percentile:
    :return: A list of percentiles of the provided data_frame
    """
    metric_names = filter_out_missing_metric_names(metric_names, data_frame)
    results = []
    for metric_name in metric_names:
        metric_column = getMetricColumn(metric_name, data_frame)
        metric_column = interpolate_data_column(metric_column)
        percentile_result = np.percentile(metric_column, percentile)

        results.append(percentile_result)
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
