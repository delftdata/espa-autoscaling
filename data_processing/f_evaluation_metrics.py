import pandas as pd
import matplotlib.pyplot as plt
import csv

query = "query-1"
auto_scaler = "HPA"
percentage = "80"

path_to_file = "../new_experiment_data_processed/full_data/" + query + "_" + auto_scaler + "_" + percentage + ".csv"
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

with open("../new_experiment_data_processed/evaluation_metrics/" + query + "_" + auto_scaler + "_" + percentage + ".csv", 'w') as f:
    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(["latency", average_latency])
    writer.writerow(["taskmanager", average_taskmanager])
    writer.writerow(["scaling_events", scaling_events])