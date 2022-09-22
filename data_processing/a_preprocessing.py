from b_get_experiment_results import scrape_data
from c_preprocess_data import combine_all_metrics
from d_plot_time_series import plot_experiments


# Set configurations heere
prometheus_ip = "35.204.161.5"
query = "query-1"
load_pattern = "cosine-50"
autoscaler = "dhalion"
metric = "05"

scrape_data(prometheus_ip, query, autoscaler, metric, load_pattern)

combine_all_metrics(query, autoscaler, metric, load_pattern)

plot_experiments(query, autoscaler, metric, load_pattern)



