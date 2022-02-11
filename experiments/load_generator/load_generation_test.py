import os
import time
import math


# use threads in java?

period = 1 / (2 * math.pi)
amplitude = 10000
limit = 10000
for i in range(1, 10):
    start_time = time.time()
    # print(start_time)

    counter = 0
    while(counter < limit):
        counter+=1
    finish_time = time.time()

    difference = finish_time - start_time
    # print(difference)
    if difference <= 1:
        time.sleep(1 - difference)
    limit = 10000 + amplitude * math.cos(period)
    period += 1

    print(counter)