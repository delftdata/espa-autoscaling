import os
import time
import math


# use threads in java?

start = 30
period = 2 * math.pi/90
amplitude = 200000
vertical_shift = 200000
limit = 100000
for i in range(1, 91):
    start_time = time.time()
    # print(start_time)

    counter = 0

    finish_time = time.time()

    difference = finish_time - start_time
    # print(difference)
    # if difference <= 1:
    #     time.sleep(1 - difference)
    limit = vertical_shift + amplitude * math.cos(period*start)
    while(counter < limit):
        counter+=1
    start += 1

    print(counter)