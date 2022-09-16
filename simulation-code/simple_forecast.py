import matplotlib.pyplot as plt
from random import randint
import math
from pyinform.blockentropy import block_entropy
import numpy as np


def sampen(L, m, r):
    N = len(L)
    B = 0.0
    A = 0.0

    # Split time series and save all templates of length m
    xmi = np.array([L[i: i + m] for i in range(N - m)])
    xmj = np.array([L[i: i + m] for i in range(N - m + 1)])

    # Save all matches minus the self-match, compute B
    B = np.sum([np.sum(np.abs(xmii - xmj).max(axis=1) <= r) - 1 for xmii in xmi])

    # Similar for computing A
    m += 1
    xm = np.array([L[i: i + m] for i in range(N - m + 1)])

    A = np.sum([np.sum(np.abs(xmi - xm).max(axis=1) <= r) - 1 for xmi in xm])

    # Return SampEn
    return -np.log(A / B)



x = []
y0 = []
y = []
y2 = []
y3 = []
y4 = []

current = 0
for i in range(1000):
    x.append(i)
    y0.append(10 + randint(-1, 1))
    current += randint(-2, 2)
    y.append(current + 100)
    y2.append(math.cos(i) * randint(0, 2) + 10)
    y3.append(math.cos(i/10) + 10)
    y4.append(2)


# print(block_entropy(y0, 1))
# print(block_entropy(y, 1))
# print(block_entropy(y2, 1))
# print(block_entropy(y3, 1))
# print(block_entropy(y4, 1))
#
print(sampen(y0, 1, 1))
print(sampen(y, 1, 1))
print(sampen(y2, 1, 1))
print(sampen(y3, 1, 1))
print(sampen(y4, 1, 1))
#
# print(sampen(y0, 10, 5))
# print(sampen(y, 10, 5))
# print(sampen(y2, 10, 5))
# print(sampen(y3, 10, 5))
# print(sampen(y4, 10, 5))

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
