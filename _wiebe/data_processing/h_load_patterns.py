import math
import random
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import os

random.seed(23)

def save_time_series(data, query, load_pattern):
    file_name = query + "_" + load_pattern
    path = '../new_load_patterns/'
    if not os.path.exists(path):
        os.makedirs(path)

    with open('../new_load_patterns/' + file_name +'.txt', "w") as text_file:
        row = ""
        for val in data:
            row += str(val) + ","
        row = row[:len(row) - 1]
        text_file.write(row)

def cosine_plot(time, query):
    cosine_period = 60
    if query == "query-1":
        amplitude = 100000
        yshift = 150000

    elif query == "query-3":
        amplitude = 25000
        yshift = 50000

    elif query == "query-11":
        amplitude = 15000
        yshift = 30000

    values = []
    indices = []
    for i in range(0, time):
        period = (2 * math.pi / cosine_period)
        val = yshift + amplitude * math.cos(period * i)
        val += random.randrange(-10000, 10000)
        values.append(val)
        indices.append(i)
    values = [int(val) for val in values]
    values = [-1*val if val < 0 else val for val in values]
    return indices, values

def random_walk(time, query):
    if query == "query-1":
        val = 150000
    elif query == "query-3":
        val = 50000
    elif query == "query-11":
        val = 30000

    values = []
    indices = []
    for i in range(0, time):
        val += random.randrange(-10000, 10000)
        values.append(val)
        indices.append(i)
    values = [int(val) for val in values]
    values = [-1*val if val < 0 else val for val in values]
    return indices, values

def increasing(time, query):
    if query == "query-1":
        magnitude = 240000
    elif query == "query-3":
        magnitude = 75000
    elif query == "query-11":
        magnitude = 150000
    initial_val = magnitude
    values = []
    indices = []
    val = 2000
    for i in range(0, time):
        val += random.randrange(int(-initial_val * (1 / 30)), int(initial_val * (1 / 22)))
        values.append(val)
        indices.append(i)
    values = [int(val) for val in values]
    values = [-1*val if val < 0 else val for val in values]
    return indices, values

def decreasing(time, query):
    if query == "query-1":
        val = 240000
    elif query == "query-3":
        val = 80000
    elif query == "query-11":
        val = 150000
    initial_val = val
    values = []
    indices = []
    val += 2000
    for i in range(0, time):
        val += random.randrange(int(-initial_val * (1 / 21)), int(initial_val * (1/28)))
        values.append(val)
        indices.append(i)
    values = [int(val) for val in values]
    values = [-1*val if val < 0 else val for val in values]
    return indices, values



# query 1
# indices1, values1 = cosine_plot(140, "query-1")
# indices2, values2 = random_walk(140, "query-1")
# indices3, values3 = increasing(140, "query-1")
# indices4, values4 = decreasing(140, "query-1")

# query 3
# indices1, values1 = cosine_plot(140, "query-3")
# indices2, values2 = random_walk(140, "query-3")
# indices3, values3 = increasing(140, "query-3")
# indices4, values4 = decreasing(140, "query-3")


# query 11
# indices1, values1 = cosine_plot(140, "query-1")
# indices2, values2 = random_walk(140, "query-1")
# indices3, values3 = increasing(140, "query-1")
# indices4, values4 = decreasing(140, "query-1")

experiment_time = 140
queries = ["query-1", "query-3", "query-11"]

for query in queries:
    print("Generating load patterns for query: " + query)
    indices1, values1 = cosine_plot(experiment_time, query)
    indices2, values2 = random_walk(experiment_time, query)
    indices3, values3 = increasing(experiment_time, query)
    indices4, values4 = decreasing(experiment_time, query)

    print("length cosine: {} negative values: {}".format(len(values1), min(values1)))
    print("length random: {} negative values: {}".format(len(values1), min(values2)))
    print("length increasing: {} negative values: {}".format(len(values1), min(values3)))
    print("length decreasing: {} negative values: {}".format(len(values1), min(values4)))

    save_time_series(values1, query, "cosine")
    save_time_series(values2, query, "random")
    save_time_series(values3, query, "increasing")
    save_time_series(values4, query, "decreasing")


# plotting the load patterns
    all_values = [values1, values2, values3, values4]
    titles = ["Cosine", "Random", "Increasing", "Decreasing"]
    fig, axs = plt.subplots(4,1, figsize=(20, 10), facecolor='w', edgecolor='k', sharex='all')
    fig.subplots_adjust(hspace = .5, wspace=.001)

    for i in range(0, 4):
        axs[i].title.set_text(titles[i])
        axs[i].plot(indices1, all_values[i], color="red")
        axs[i].grid()
        axs[i].set_ylabel("Records per second")

    axs[3].set_xlabel("Minutes")
    plt.show()

# name = "load_patterns"
# path = "../figures/other/" + name + ".png"
# plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [18.0, 10.0]]), dpi=600)