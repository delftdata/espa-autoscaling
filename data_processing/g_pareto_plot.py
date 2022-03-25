import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import pandas as pd
from adjustText import adjust_text
import os

load_pattern = "cosine"
path = "../experiment_data_processed/full_data/cosine"


files = os.listdir(path)

fig, ax = plt.subplots()
color_per_autoscaler ={"HPA": "red", "varga": "purple", "dhalion": "green", "ds2":"black"}

latency_per_autoscaler = []
taskmanagers_per_autoscaler = []
texts = []

for file in files:
    file_info = file.split("_")
    query = file_info[0]
    auto_scaler = file_info[1]
    metric = file_info[2]
    df = pd.read_csv("../experiment_data_processed/full_data/" + load_pattern + "/" + file)
    latency_list = df['latency'].tolist()
    taskmanager_list = df['taskmanager'].tolist()
    average_latency = sum(latency_list) / len(latency_list)
    average_taskmanager = sum(taskmanager_list) / len(taskmanager_list)
    latency_per_autoscaler.append(average_latency)
    taskmanagers_per_autoscaler.append(average_taskmanager)
    ax.scatter(average_taskmanager,average_latency, s=20, color=color_per_autoscaler[auto_scaler], label=auto_scaler)
    # ax.annotate(auto_scaler + " " + HPA_data[i], (average_taskmanager, average_latency-1), ha='center')
    texts.append(ax.text(average_taskmanager, average_latency, auto_scaler + " " + metric, ha='center', va='center'))

# adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))

plt.legend(loc=(1.02,0.85), labelspacing=1)
plt.grid()
plt.xlabel("Average number of taskmanagers")
plt.ylabel("Average latency (s)")
plt.show()



#
# query = "query-1"
#
# HPA_data = ["50", "70", "90", "50", "70", "90", "01", "02", "03"]
# latency_per_autoscaler = []
# taskmanagers_per_autoscaler = []
#
# color_per_autoscaler ={"HPA": "red", "varga": "purple", "dhalion": "green"}
#
# fig, ax = plt.subplots()
#
# auto_scaler = "HPA"
# texts = []
# for i in range(0, 9):
#     if i == 3:
#         auto_scaler = "varga"
#     elif i == 6:
#         auto_scaler = "dhalion"
#     df = pd.read_csv("../experiment_data_processed/full_data/" + query + "_" + auto_scaler + "_" + HPA_data[i] + ".csv")
#     latency_list = df['latency'].tolist()
#     taskmanager_list = df['taskmanager'].tolist()
#     average_latency = sum(latency_list) / len(latency_list)
#     average_taskmanager = sum(taskmanager_list) / len(taskmanager_list)
#     latency_per_autoscaler.append(average_latency)
#     taskmanagers_per_autoscaler.append(average_taskmanager)
#     ax.scatter(average_taskmanager,average_latency, s=20, color=color_per_autoscaler[auto_scaler], label=auto_scaler if i % 3 == 0 else "")
#     # ax.annotate(auto_scaler + " " + HPA_data[i], (average_taskmanager, average_latency-1), ha='center')
#     texts.append(ax.text(average_taskmanager, average_latency, auto_scaler + " " + HPA_data[i], ha='center', va='center'))
#
# adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
# # adjust_text(texts, only_move={'points':'y', 'text':'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
#
# plt.legend(loc=(1.02,0.85), labelspacing=1)
# plt.grid()
# plt.xlabel("Average number of taskmanagers")
# plt.ylabel("Average latency (s)")
# # plt.show()
#
#
# # color =["red", "cyan", "purple", "green"]
#
#
# path = "../figures_final/cosine/query-1/pareto_figs/" + query + "_pareto.png"
# plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [6.0, 5.0]]), dpi=600)