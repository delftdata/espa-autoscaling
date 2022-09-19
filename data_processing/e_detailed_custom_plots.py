import pandas as pd
import matplotlib.pyplot as plt

# metrics = ["input_rate", "taskmanager", "latency", "lag", "throughput" , "CPU_load", "backpressure", "busy_time", "idle_time"]
from matplotlib.transforms import Bbox

query = "query-1"
auto_scaler = "dhalion"
percentage = "05"

path_to_file = "../new_experiment_data_processed/full_data/cosine/" + query + "/" + query + "_" + auto_scaler + "_" + percentage + ".csv"
df = pd.read_csv(path_to_file)

metrics = ["input_rate", "taskmanager", "latency", "throughput"]
# metrics = ["input_rate", "taskmanager", "latency", "throughput", "backpressure"]
# metrics = ["input_rate", "taskmanager", "lag", "latency", "throughput", "CPU_load", "busy_time", "idle_time", "backpressure"]

meric_names = {"input_rate": "Kafka input rate (records per second)", "taskmanager": "Taskmanagers", "latency":"Latency (s)", "throughput":"Throughput (records per second)", "backpressure":"Backpressure (ms)", "CPU_load":"CPU utilization", "lag": "Lag (records)", "busy_time": "Busy time (ms)", "idle_time":"Idle time (ms)"}
ylabel = {"input_rate": "records per seconds", "taskmanager": "# taskmanagers", "latency": "seconds", "CPU_load":"", "backpressure": "ms"}
fig, axs = plt.subplots(len(metrics),1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
fig.subplots_adjust(hspace = .5, wspace=.001)

for i in range(0, len(metrics)):
    axs[i].plot(df["minutes"], df[metrics[i]], color="red")
    axs[i].title.set_text(meric_names[metrics[i]])
    # axs[i].set_yticks([], minor=False)
    max_val = max(df[metrics[i]].tolist())
    min_val = min(df[metrics[i]].tolist())
    axs[i].set_ylim([0 , max_val * 1.2])
    # axs[i].set_ylabel(ylabel[metrics[i]])
    axs[i].grid()

axs[len(metrics) - 1].set_xlabel("Minutes")


# plt.show()
path = "../new_figures_final/cosine/" + query + "/detailed_figs/" + query + "_" + auto_scaler + "_" + percentage + ".png"
plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [18.0, 10.0]]), dpi=600)