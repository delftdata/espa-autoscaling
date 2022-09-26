import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import pandas as pd
from adjustText import adjust_text
import os
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset


def pareto_plot(query, zoomed, latency_limit, zoomed_latency_limit):
    load_pattern = "cosine"
    path = "../new_experiment_data_processed/full_data/" + load_pattern + "/" + query
    files = os.listdir(path)
    fig, ax = plt.subplots()
    color_per_autoscaler = {"HPA": "red", "vargav1": "purple", "vargav2": "orange", "dhalion": "green", "ds2": "black",
                            "ds2-adapted-reactive": "pink", "ds2-original-reactive": "brown",
                            "ds2-adapted-non-reactive": "blue", "ds2-original-non-reactive": "blue"}
    marker_per_autoscaler = {"HPA": "o", "vargav1": "*", "vargav2": "P", "dhalion": "X", "ds2": "P",
                             "ds2-adapted-reactive": "D", "ds2-original-reactive": "s",
                             "ds2-adapted-non-reactive": "blue", "ds2-original-non-reactive": "blue"}
    rename = {"HPA": "HPA", "vargav1": "Vargav1", "vargav2": "Vargav2", "dhalion": "Dhalion-adapted",
              "ds2-original-reactive": "DS2-modern", "ds2-adapted-reactive": "DS2-modern-adapted"}

    latency_per_autoscaler = []
    taskmanagers_per_autoscaler = []
    texts = []
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
        df = pd.read_csv("experiment_data/full_data/" + load_pattern + "/" + query + "/" + file)
        latency_list = df['latency'].tolist()
        taskmanager_list = df['taskmanager'].tolist()
        average_latency = sum(latency_list) / len(latency_list)
        average_taskmanager = sum(taskmanager_list) / len(taskmanager_list)
        if average_latency > latency_limit:
            continue
        if zoomed and average_latency > zoomed_latency_limit:
            continue
        latency_per_autoscaler.append(average_latency)
        taskmanagers_per_autoscaler.append(average_taskmanager)
        ax.scatter(average_taskmanager, average_latency, s=50, color=color_per_autoscaler[auto_scaler],
                   marker=marker_per_autoscaler[auto_scaler],
                   label=rename[auto_scaler] if auto_scaler not in seen else "")
        # ax.annotate(metric, (average_taskmanager, average_latency), ha='center', size=6)
        seen.add(auto_scaler)
        texts.append(ax.text(average_taskmanager, average_latency, metric, ha='right', va='top', size=10))

    if zoomed:
        plt.ylim([0, zoomed_latency_limit])
        plt.xlim([0, 16])
    else:
        plt.ylim([0, latency_limit])
        plt.xlim([0, 16])

    adjust_text(texts, only_move={'points': 'y', 'texts': 'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0))
    plt.legend(loc=(1.02, 0.5), labelspacing=1)
    plt.grid()
    plt.xlabel("Average number of taskmanagers")
    plt.ylabel("Average latency (s)")

    path = "experiment_data/pareto_plots/" + load_pattern + "/" + query + "/pareto_figs"
    if not os.path.exists(path):
        os.makedirs(path)

    if zoomed:
        filepath = path + "/" + query + "_pareto_zoomed.png"
    else:
        filepath = path + "/" + query + "_pareto.png"
    plt.savefig(filepath, format="png", bbox_inches=Bbox([[0, 0], [8.0, 5.0]]), dpi=600)


pareto_plot("query-1", False, 50, 20)
#
pareto_plot("query-1", True, 50, 20)

# pareto_plot("query-3", False, 200, 50)
#
# pareto_plot("query-3", True, 200, 50)

# pareto_plot("query-11", False, 100, 20)

# pareto_plot("query-11", True, 100, 20)
