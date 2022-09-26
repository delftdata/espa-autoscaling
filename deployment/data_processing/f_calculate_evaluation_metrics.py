import pandas as pd
import matplotlib.pyplot as plt
import csv
import os


def calulate_evaluation_metrics(query, auto_scaler, percentage, load_pattern="cosine-60"):
    path_to_file = f"/experiment_data/full_data/{load_pattern}/{query}/{query}_{auto_scaler}_{percentage}.csv"
    df = pd.read_csv(path_to_file)

    taskmanager = df['taskmanager'].tolist()
    latency = df['latency'].tolist()

    previous_number_taskmanagers = taskmanager[0]
    scaling_events = 0
    for val in taskmanager:
        if val != previous_number_taskmanagers:
            scaling_events += 1
        previous_number_taskmanagers = val

    average_latency = sum(latency) / len(latency)
    average_taskmanager = sum(taskmanager) / len(taskmanager)

    path = f"/experiment_data/evaluation_metrics/{load_pattern}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + f"/{query}_{auto_scaler}_{percentage}.csv", 'w') as f:
        # create the csv writer
        writer = csv.writer(f)
        writer.writerow(["latency", average_latency])
        writer.writerow(["taskmanager", average_taskmanager])
        writer.writerow(["scaling_events", scaling_events])