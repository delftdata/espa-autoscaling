import pandas as pd

pd.options.display.max_columns = None
import os

"""
Put together all data fetched from prometheus server
"""


def combine_all_metrics(query, auto_scaler, percentage, load_pattern):
    metrics = ["backpressure", "busy_time", "CPU_load", "idle_time", "lag", "latency", "taskmanager", "throughput"]

    path_to_files = "experiment_data/individual_data/" + query + "/" + load_pattern + "/" + auto_scaler + "/" + percentage + "/"
    input_data = pd.read_csv(path_to_files + "input_rate.csv")

    # convert timestamps to seconds
    input_data["datetime"] = pd.to_datetime(input_data['timestamp'], format="%Y/%m/%d")

    # remove first files of experiment
    input_data = input_data.loc[input_data['value'] != 0]

    # get number of minutes and seconds since start of experiment
    input_data = input_data.reset_index()
    input_data['seconds'] = input_data.index.values * 15
    input_data['minutes'] = input_data.index.values * 0.25

    # filter tail of dataframe
    input_data = input_data.loc[input_data['minutes'] <= 140]

    # remove column
    input_data = input_data.drop(labels="__name__", axis="columns")

    # rename 'value' to metric name
    input_data = input_data.rename(columns={"value": "input_rate"})

    for metric in metrics:
        df = pd.read_csv(path_to_files + metric + ".csv")
        df = df.drop(labels="__name__", axis="columns")
        df = df.rename(columns={"value": metric})
        input_data = input_data.join(df.set_index('timestamp'), on="timestamp", how='left')

    metrics = ["input_rate", "backpressure", "busy_time", "CPU_load", "idle_time", "lag", "latency", "taskmanager",
               "throughput"]

    for metric in metrics:
        input_data[metric] = input_data[metric].interpolate()

    input_data = input_data.fillna(0)

    path = "experiment_data/full_data/" + load_pattern + "/" + query
    if not os.path.exists(path):
        os.makedirs(path)
    input_data.to_csv(path + "/" + query + "_" + auto_scaler + "_" + percentage + ".csv")
