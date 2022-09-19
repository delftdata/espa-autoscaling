import pandas as pd
from datetime import datetime
pd.options.display.max_columns = None

# query = "query-1"
# auto_scaler = "vargav1"
# percentage = "70"


def combine_all_metrics(query, auto_scaler, percentage, load_pattern):
    metrics = ["backpressure", "busy_time", "CPU_load", "idle_time", "lag", "latency", "taskmanager", "throughput"]

    path_to_files = "../new_experiment_data/" + query + "/" + load_pattern + "/" + auto_scaler + "/" + percentage + "/"

    input_data = pd.read_csv(path_to_files + "input_rate.csv")



    # convert timestamps to seconds
    input_data["datetime"] = pd.to_datetime(input_data['timestamp'], unit='s')

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
        df = pd.read_csv(path_to_files + metric  + ".csv")
        df = df.drop(labels="__name__", axis="columns")
        df = df.rename(columns={"value": metric})
        input_data = input_data.join(df.set_index('timestamp'), on="timestamp", how='left')


    metrics = ["input_rate", "backpressure", "busy_time", "CPU_load", "idle_time", "lag", "latency", "taskmanager", "throughput"]

    for metric in metrics:
        input_data[metric] = input_data[metric].interpolate()

    input_data = input_data.fillna(0)

    input_data.to_csv("../new_experiment_data_processed/full_data/" + load_pattern + "/" + query + "/" + query + "_" + auto_scaler + "_" + percentage + ".csv")

