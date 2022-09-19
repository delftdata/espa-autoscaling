import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox



def plot_experiments(query, auto_scaler, percentage, load_pattern):
    path_to_file = "../new_experiment_data_processed/full_data/" + load_pattern + "/" + query + "/" + query + "_" + auto_scaler + "_" + percentage + ".csv"
    df = pd.read_csv(path_to_file)

    metrics = ["input_rate", "taskmanager", "latency", "lag", "throughput" , "CPU_load", "backpressure", "busy_time", "idle_time"]


    fig, axs = plt.subplots(9,1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace = .5, wspace=.001)
    for i in range(0, len(metrics)):
        axs[i].plot(df["minutes"], df[metrics[i]], color="red")
        axs[i].title.set_text(metrics[i])
        # axs[i].set_yticks([], minor=False)
        max_val = max(df[metrics[i]].tolist())
        min_val = min(df[metrics[i]].tolist())
        axs[i].set_ylim([0 , max_val * 1.2])
        axs[i].grid()

    axs[len(metrics) - 1].set_xlabel("Minutes")

    # plt.show()
    path = "../new_figures_final/" + load_pattern + "/" + query + "/experiment_figs/" + query + "_" + load_pattern + "_" + auto_scaler + "_" + percentage + ".png"
    plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [18.0, 10.0]]), dpi=600)