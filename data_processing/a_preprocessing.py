from b_get_experiment_results import scrape_data
from c_preprocess_data import combine_all_metrics
from d_plot_time_series import plot_experiments

prometheus_ip = "35.203.60.252"
query = "query-3"
load_pattern = "cosine"
autoscaler = "ds2-adapted-reactive"
metric = "66"

scrape_data(prometheus_ip, query, autoscaler, metric, load_pattern)

combine_all_metrics(query, autoscaler, metric, load_pattern)

plot_experiments(query, autoscaler, metric, load_pattern)



