import matplotlib.pyplot as plt
import math
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")


time, produce_rate, lag, consume_rate, servers = [], [], [], [], []
time.append(400),
produce_rate.append(0)
lag.append(0)
consume_rate.append(0)
servers.append(3)

number_of_servers = 4
max_rate_of_server = 5000
frecuency = 0.05
time_period = 600
offset = 10000
amplitude = 5000
rescale_time = 5
pause = 0
rescale_threshold = 10000
rescale_cooldown = 30

cooldown = 0

# forcasting parameters
forecast_steps = 15

lag_one_timestep = 0

training_time_period = 400
history = []

# creat historical data for the model
for t in range(0, training_time_period):
    history.append(offset + amplitude * math.cos(frecuency * t))



for t in range(training_time_period, training_time_period + time_period):
    print(t)
    time.append(t)
    if cooldown > 0:
        cooldown -= 1

    produce_one_timestep = offset + amplitude * math.cos(frecuency * t)
    lag_one_timestep = lag[-1] + produce_one_timestep
    history.append(produce_one_timestep)

    # fit the model
    model = ARIMA(history, order=(4, 0, 0))
    model_fit = model.fit()
    output = model_fit.forecast(steps=forecast_steps)

    if pause == 0:
        consume_one_timestep = min(produce_one_timestep + lag[-1], (number_of_servers * max_rate_of_server))
        lag_one_timestep = lag[-1] - consume_one_timestep + produce_one_timestep

        # scaling decision
        future_lag = lag[-1]
        for produce_rate_future in output:
            consume_one_timestep_future = min(produce_rate_future + future_lag, (number_of_servers * max_rate_of_server))
            future_lag += produce_rate_future - consume_one_timestep_future

        if future_lag > rescale_threshold and cooldown == 0:
            number_of_servers += 1
            pause = rescale_time
            cooldown = rescale_cooldown
        elif future_lag <= rescale_threshold and cooldown == 0 and ((max_rate_of_server*number_of_servers) - produce_rate_future > max_rate_of_server):
            number_of_servers -= 1
            pause = rescale_time
            cooldown = rescale_cooldown
    else:
        pause -= 1
        consume_one_timestep = 0

    lag.append(lag_one_timestep)
    produce_rate.append(produce_one_timestep)
    consume_rate.append(consume_one_timestep)
    servers.append(number_of_servers)



fig, axs = plt.subplots(3)

axs[0].plot(time, produce_rate, label='Produce rate')
axs[0].plot(time, consume_rate, label='Consume rate')
axs[1].plot(time, lag)
axs[2].plot(time, servers)

axs[2].set_xlabel("Time")

axs[0].title.set_text('Records produced and consumed per second')
axs[1].title.set_text('Consumer lag')
axs[2].title.set_text('Number of task managers')

axs[0].grid()
axs[1].grid()
axs[2].grid()

axs[0].legend()

fig.tight_layout()

plt.show()
