from b_get_experiment_results import scrape_data
from c_preprocess_data import combine_all_metrics
from d_plot_time_series import plot_experiments

prometheus_ip = "34.147.46.242"
query = "query-11"
load_pattern = "cosine"
autoscaler = "vargav2"
metric = "30"

scrape_data(prometheus_ip, query, autoscaler, metric, load_pattern)

combine_all_metrics(query, autoscaler, metric, load_pattern)

plot_experiments(query, autoscaler, metric, load_pattern)



