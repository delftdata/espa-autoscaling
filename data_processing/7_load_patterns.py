import math
import random
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

random.seed(12)
def cosine_plot(time):
    cosine_period = 90
    values = []
    indices = []
    for i in range(0, time):
        val = math.cos(i)
        period = (2 * math.pi / cosine_period)
        val = 120000 + 80000 * math.cos(period * i)
        val += random.randrange(-10000, 10000)
        values.append(val)
        indices.append(i)
    return indices, values

def random_walk(time):
    values = []
    indices = []
    val = 100000
    for i in range(0, time):
        val += random.randrange(-10000, 10000)
        values.append(val)
        indices.append(i)
    return indices, values

def increasing(time):
    values = []
    indices = []
    val = 0
    for i in range(0, time):
        val += random.randrange(-8000, 12000)
        values.append(val)
        indices.append(i)
    return indices, values

def decreasing(time):
    values = []
    indices = []
    val = 240000
    for i in range(0, time):
        val += random.randrange(-12000, 8000)
        values.append(val)
        indices.append(i)
    return indices, values


indices1, values1 = cosine_plot(140)
indices2, values2 = random_walk(140)
indices3, values3 = increasing(140)
indices4, values4 = decreasing(140)

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
# plt.show()

name = "load_patterns"
path = "../figures/other/" + name + ".png"
plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [18.0, 10.0]]), dpi=600)