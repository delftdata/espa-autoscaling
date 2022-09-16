import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from scipy.integrate import simps

def preprocess(df):
    df['time'] = pd.to_datetime(df['time'])
    df["time"] = df["time"].apply(lambda x: str(x.time()))
    return df


data_tm = pd.read_csv("taskmanagers.csv", names=["time", "metric"])
data_lag = pd.read_csv("consumer_lag.csv", names=["time", "metric"])
data_lag = data_lag.fillna(0)

data_tm = preprocess(data_tm)
data_lag = preprocess(data_lag)

list_tm_data_time = data_tm["time"].tolist()

list_tm_data_metric = data_tm["metric"].tolist()
list_lag_metric = data_lag["metric"].tolist()

min_time = datetime.strptime(list_tm_data_time[0], '%H:%M:%S')
max_time = datetime.strptime(list_tm_data_time[-1], '%H:%M:%S')
print(min_time)
print(max_time)
print(max_time - min_time)

previous_number_taskmanagers = list_tm_data_metric[0]
scaling_events = 0
for val in list_tm_data_metric:
    if val != previous_number_taskmanagers:
        scaling_events += 1
    previous_number_taskmanagers = val


print("Compute per hour used: {:.2f} taskmanagers".format(sum(data_tm["metric"].tolist()) / 240))

print("Avg lag over 1 hour period experienced {:.2f} records".format(sum(data_lag["metric"].tolist()) / 240))

print("There were {} scaling events".format(scaling_events))

