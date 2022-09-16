import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import pandas as pd
from adjustText import adjust_text
import os
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

def number_of_rescales(taskmanager):
    previous_number_taskmanagers = taskmanager[0]
    scaling_events = 0
    for val in taskmanager:
        if val != previous_number_taskmanagers:
            scaling_events += 1
        previous_number_taskmanagers = val
    return scaling_events

query = "query-11"
load_pattern = "cosine"
path = "../experiment_data_processed/full_data/" + load_pattern + "/" + query
files = os.listdir(path)


pd.set_option('precision', 2)

rename = {"HPA": "HPA", "vargav1": "Vargav1", "vargav2": "Vargav2", "dhalion": "Dhalion-adapted",
          "ds2-original-reactive": "DS2-modern", "ds2-adapted-reactive": "DS2-modern-adapted"}
name = []
metric_per_autoscaler = []
latency_per_autoscaler = []
taskmanagers_per_autoscaler = []
combined_per_autoscaler = []
rescales_per_autoscaler = []
seen = set()
for file in files:
    file_info = file.split("_")
    query = file_info[0]
    auto_scaler = file_info[1]
    if "non" in auto_scaler:
        continue
    metric = file_info[2].replace(".csv", "")
    if "i" in metric:
        continue
    df = pd.read_csv("../experiment_data_processed/full_data/" + load_pattern + "/" + query + "/" + file)
    latency_list = df['latency'].tolist()
    taskmanager_list = df['taskmanager'].tolist()
    average_latency = sum(latency_list) / len(latency_list)
    average_taskmanager = sum(taskmanager_list) / len(taskmanager_list)
    rescales = number_of_rescales(df['taskmanager'].tolist())
    name.append(rename[auto_scaler])
    metric_per_autoscaler.append(metric)
    taskmanagers_per_autoscaler.append(average_taskmanager)
    latency_per_autoscaler.append(average_latency)
    combined_per_autoscaler.append(average_latency + average_taskmanager)
    rescales_per_autoscaler.append(rescales)

    # print(auto_scaler + " " + metric + " " + "{:.2f} {:.2f} {:.2f} {:.0f}".format(average_latency, average_taskmanager, average_latency + average_taskmanager, rescales))

data = pd.DataFrame({"Auto-scaler": name, "Metric value": metric_per_autoscaler, "Latency (s)": latency_per_autoscaler, "Taskmanagers": taskmanagers_per_autoscaler, "Latency + Taskmanagers": combined_per_autoscaler, "Scaling operations": rescales_per_autoscaler})
data = data.sort_values(by="Latency + Taskmanagers")
print(data.to_string(index=False))