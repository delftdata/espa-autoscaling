import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import pandas as pd
from adjustText import adjust_text
import os
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset


load_pattern = "cosine"
query = "query-3"
path = "../experiment_data_processed/full_data/" + load_pattern + "/" + query


files = os.listdir(path)

fig, ax = plt.subplots()
# color_per_autoscaler ={"HPA": "red", "vargav1": "purple","vargav2":"orange", "dhalion": "green", "ds2":"black"}
color_per_autoscaler ={"HPA": "red", "vargav1": "purple","vargav2":"orange", "dhalion": "green", "ds2":"black", "ds2-adapted-reactive": "pink", "ds2-original-reactive":"brown", "ds2-adapted-non-reactive":"blue", "ds2-original-non-reactive":"blue"}


latency_per_autoscaler = []
taskmanagers_per_autoscaler = []
texts = []

for file in files:
    file_info = file.split("_")
    query = file_info[0]
    auto_scaler = file_info[1]
    metric = file_info[2].replace(".csv", "")
    df = pd.read_csv("../experiment_data_processed/full_data/" + load_pattern + "/" + query + "/" + file)
    latency_list = df['latency'].tolist()
    taskmanager_list = df['taskmanager'].tolist()
    average_latency = sum(latency_list) / len(latency_list)
    average_taskmanager = sum(taskmanager_list) / len(taskmanager_list)
    latency_per_autoscaler.append(average_latency)
    taskmanagers_per_autoscaler.append(average_taskmanager)
    ax.scatter(average_taskmanager,average_latency, s=20, color=color_per_autoscaler[auto_scaler], label=auto_scaler + "_" + metric)
    texts.append(ax.text(average_taskmanager, average_latency, auto_scaler + " " + metric, ha='center', va='center', size=6))

plt.ylim([0,100])
plt.xlim([0,16])
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
plt.legend(loc=(1.02,0), labelspacing=1)
plt.grid()
plt.xlabel("Average number of taskmanagers")
plt.ylabel("Average latency (s)")

# Make the zoom-in plot:
# axins = zoomed_inset_axes(ax, 3, loc=1) # zoom = 2
# axins.scatter(1,1)
# axins.set_xlim(0, 5)
# axins.set_ylim(0, 5)
# plt.xticks(visible=False)
# plt.yticks(visible=False)
# plt.draw()
# plt.show()

path = "../figures_final/" + load_pattern + "/" + query + "/pareto_figs/" + query + "_pareto.png"
plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [8.0, 5.0]]), dpi=600)


#
# query = "query-1"
#
# HPA_data = ["05", "70", "90", "05", "70", "90", "01", "02", "03"]
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