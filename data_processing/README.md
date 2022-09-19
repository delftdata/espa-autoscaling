# Data processing

This folder contains 8 files used for data processing.

# Initialization
To fetch data from the prometheus server, first install the dependencies:
```
pip install -r requirements.txt
```

# Fetch data
To fetch data from the prometheus server and process them, perform the following steps.

## Set configurations in a_processing.py
a_processing.py requires the following settings:
* prometheus_ip: IP of prometheus server
* query = executed query {query_1, query_3, query_11}
* load_pattern = used load pattern {cosine, decreasing, increasing} 
* autoscaler = autoscaler {dhalion, ds2-adapted, ds2-original, HPA, vargav1, varav2}
* metric = parameter used for autoscaler

After setting the correct settings, run a_processing.py
```
python a_processing.py
```

This should download all metrics, combine them in a single script and load them into a single graph.
This is done by the following scripts
* a_preprocessing.py
* b_get_experiment_results.py
* c_preprocess_data.py
* d_plot_time_series.py

The other scripts can be run individually to create custom graphs.
All scripts are explained in more detail down below.


# Data processing scripts
##a_preprocessing.py
Contains experiment configurations and executes the following scripts:
* b_get_experiment_results.py
* c_preprocess_data.py
* d_plot_time_series.py

##b_get_experiment_results.py
Downloads all metrics from the server and saves them in ../{new_}experiments/

##c_preprocess_data.py
Combines all metrics fetched by b_get_experiment_results.py and combines them into a single table.
This table is then stored at ../{new_}figures_final)/{load_pattern}/{query}/experiment_figs/

##d_plot_time_series.py
Fetches the table created by c_preprocess_data.py and visualises it in a single plot.
This plot is stored at .../{new_}figures_final)/{load_pattern}/{query}/detailed_figs/

##e_detailed_cusom_plots.py
Create a plot with a select number of metrics.
1. Set the following configurations: query, auto_scaler, and percentage.
2. Set the metrics variable to the metrics that should be plotted. 
   1. The following metrics are available: ["input_rate", "taskmanager", "latency", "lag", "throughput" , "CPU_load", "backpressure", "busy_time", "idle_time"]
The metrics are then stored in: ../{new_}figures_final/

##f_evaluation_metrics.py
Calculate the evaluation metrics of an experimental run
1. Set the following configurations: query, auto_scaler, percentage, and load_pattern
2. Run the script
The evaluation metrics are stored in ../{new_}experiment_data_processed/evaluation_metrics/

##g_pareto_plot.py
Create a pareto plot of all autoscalers given a specified load_pattern and query
1. Set load_pattern in pareto_plot function
2. Add function call with as parameters the query, a boolean whether to zoom, latency_limit and zoom_latency_limit
3. Run the script
The result is stored at ../{new_}figures_final/{load_pattern}/{query}/pareto_figs/

##h_load_patterns.py
Calculate load_patterns of the current data
1. set experiment_time and queries to investigate
2. Run the script
The result is stored at ../{new_}load_patterns/

##i_tables.py
Get a summary of all experimental runs
1. Run the script
The result is listed as output in the console

