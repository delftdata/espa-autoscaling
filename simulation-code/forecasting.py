from statsmodels.tsa.arima.model import ARIMA
import math
import matplotlib.pyplot as plt
import random
import pandas as pd

# fix the index this is a big mess, steps doe apear to be sort of working


number_of_servers = 4
max_rate_of_server = 5000
frecuency = 0.05
time_period = 400
offset = 10000
amplitude = 5000
rescale_time = 5
pause = 0
rescale_threshold = 10000
rescale_cooldown = 30
random_amplitude = 100
x_index = []
x = 0
time_period = 300

points = []

for t in range(0, time_period):
    x_index.append(x)
    x += 1
    points.append(offset + amplitude * math.cos(frecuency * t) + random.uniform(-0.5, 0.5)*random_amplitude)

predictions = []
actual = []
history = points

forecast_steps = 100

forecast = x_index[-1] + forecast_steps
forecast_index = [100 + x for x in range(1, forecast_steps + 1)]

model = ARIMA(history, order=(4, 0, 0))
model_fit = model.fit()
output = model_fit.forecast(steps=forecast_steps)

plt.plot(forecast_index, output, label='predictions')
plt.plot(x_index, history, label='real')

plt.legend()
plt.grid()
plt.show()

#
# for t in range(time_period, 2 * time_period):
#     model = ARIMA(history, order=(2, 0, 0))
#     model_fit = model.fit()
#     output = model_fit.forecast(steps=forecast_steps)
#     print(output)
#     yhat = output[-1]
#     predictions.append(yhat)
#     obs = offset + amplitude * math.cos(frecuency * t)
#     history.append(obs)
#     actual.append(obs)
#     x_index.append(x)
#     x += 1
#     forecast_index.append(forecast)
#     forecast += 1
#
# plt.plot(forecast_index, predictions, label='predictions')
# plt.plot(x_index, history, label='real')
#
# plt.legend()
# plt.grid()
# plt.show()
