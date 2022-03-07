import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

query = "query-1"


taskmanagers = [3.5, 4.7, 5.3, 2.1]
latency = [1.1, 4.4, 7.7, 3.6]
scales = [200, 300, 59, 450]
labels = ["HPA", "Dhalion", "Varga", "DS2"]
color =["red", "cyan", "purple", "green"]


fig, ax = plt.subplots()

names = ["Aggresive", "Conservative", "Medium", "Medium"]
for i, txt in enumerate(names):
    ax.scatter(taskmanagers[i],latency[i], s=scales[i],color=color[i], label=labels[i])
    ax.annotate(txt, (taskmanagers[i], latency[i]-0.1), ha='center')

plt.grid()
plt.xlabel("Average number of taskmanagers")
plt.ylabel("Average latency (s)")
plt.legend(loc=(1.02,0.85), labelspacing=1)
# plt.show()

path = "../figures/cosine/query-1/pareto_figs/" + query + "_pareto.png"
plt.savefig(path, format="png", bbox_inches=Bbox([[0, 0], [7.0, 5.0]]), dpi=600)