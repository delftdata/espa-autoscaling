import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def preprocess(df):
    df['time'] = pd.to_datetime(df['time'])
    df["time"] = df["time"].apply(lambda x: str(x.time()))
    return df


data_input_rate = pd.read_csv("input_rate.csv", names=["time", "metric"])
data_tm = pd.read_csv("taskmanagers.csv", names=["time", "metric"])
data_lag = pd.read_csv("consumer_lag.csv", names=["time", "metric"])
data_throughput = pd.read_csv("throughput.csv", names=["time", "metric"])

data_input_rate = preprocess(data_input_rate)
data_tm = preprocess(data_tm)
data_lag = preprocess(data_lag)
data_throughput = preprocess(data_throughput)


print(data_tm)

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
ax3.title.set_text('Throughput')

ax4.plot(data_lag["time"], data_lag["metric"], color="red")
ax4.set_ylabel("Records")
ax4.set_yticks([], minor=False)
ax4.title.set_text('Consumer Lag')

ax4.set_xticks(np.arange(0, len(data_lag["time"].tolist())+1, 15))

plt.show()