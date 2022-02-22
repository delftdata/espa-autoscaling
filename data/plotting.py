import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def preprocess(df, num_records):
    df['time'] = pd.to_datetime(df['time'])
    df["time"] = df["time"].apply(lambda x: str(x.time()))
    df = df.tail(num_records)
    return df

# folder = "./bad-hpa-experiment/"
folder = "./no_scale_down/"
num_records = 300

data_input_rate = pd.read_csv(folder + "input_rate.csv", names=["time", "metric"])
data_tm = pd.read_csv(folder + "taskmanagers.csv", names=["time", "metric"])
data_lag = pd.read_csv(folder + "consumer_lag.csv", names=["time", "metric"])
data_throughput = pd.read_csv(folder + "CPU_load.csv", names=["time", "metric"])

data_input_rate = preprocess(data_input_rate, num_records)
data_tm = preprocess(data_tm, num_records)
data_lag = preprocess(data_lag, num_records)
data_throughput = preprocess(data_throughput, num_records)


f, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, sharex='all')


ax1.plot(data_input_rate["time"], data_input_rate["metric"], color="red")
ax1.set_ylabel("Records per second")
ax1.set_yticks([], minor=False)
ax1.title.set_text('Load')

ax2.plot(data_tm["time"], data_tm["metric"], color="red")
ax2.set_ylabel("Taskmanagers")
ax2.set_yticks([], minor=False)
ax2.title.set_text('Number of Taskmanagers')

ax3.plot(data_throughput["time"], data_throughput["metric"], color="red")
ax3.set_ylabel("Records per second")
ax3.set_yticks([], minor=False)
ax3.title.set_text('CPU load')

ax4.plot(data_lag["time"], data_lag["metric"], color="red")
ax4.set_ylabel("Records")
ax4.set_yticks([], minor=False)
ax4.title.set_text('Consumer Lag')

ax4.set_xticks(np.arange(0, len(data_lag["time"].tolist())+1, 30))

plt.savefig("./figures/" + folder[2:len(folder)-1], dpi='figure', format=None, metadata=None,
        bbox_inches=None, pad_inches=0.1,
        facecolor='auto', edgecolor='auto',
        backend=None)
plt.show()
