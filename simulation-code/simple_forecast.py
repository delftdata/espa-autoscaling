import matplotlib.pyplot as plt
from random import randint
import math



x = []
y = []
y2 = []
y3 = []

current = 0
for i in range(100):
    x.append(i)
    current += randint(-3, 3)
    y.append(current)
    y2.append(math.cos(i) * randint(0, 2))
    y3.append(math.cos(i))



fig, axs = plt.subplots(3)

axs[0].plot(x, y)
axs[1].plot(x, y2)
axs[2].plot(x, y3)

axs[2].set_xlabel("Time")

axs[0].title.set_text('Hard')
axs[1].title.set_text('In between')
axs[2].title.set_text('Easy')

axs[0].grid()
axs[1].grid()
axs[2].grid()

fig.tight_layout()

plt.show()
