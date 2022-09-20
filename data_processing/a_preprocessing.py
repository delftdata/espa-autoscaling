from b_get_experiment_results import scrape_data
from c_preprocess_data import combine_all_metrics
from d_plot_time_series import plot_experiments


# Set configurations heere
prometheus_ip = "34.91.123.186"
query = "load-patterns"
load_pattern = "cosine-period"
autoscaler = "none"
metric = "20"

scrape_data(prometheus_ip, query, autoscaler, metric, load_pattern)

combine_all_metrics(query, autoscaler, metric, load_pattern)

plot_experiments(query, autoscaler, metric, load_pattern)



