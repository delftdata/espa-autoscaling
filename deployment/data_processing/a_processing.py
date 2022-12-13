from PrometheusManager import scrape_data
from c_combine_all_metrics import combine_all_metrics
from d_plot_experiments import plot_experiments
from e_plot_detailed_plot import plot_detailed_plot
from f_calculate_evaluation_metrics import calulate_evaluation_metrics

# Set configurations heere
DETAILED_METRICS = ["input_rate", "taskmanager", "latency", "throughput"]


def process_data(prometheus_ip, query, autoscaler, load_pattern, metric, experiment_time_minutes):
    # Get data from prometheus
    scrape_data(prometheus_ip, query, autoscaler, metric, load_pattern, experiment_time_minutes)

    # Combine all metrics in a single table
    combine_all_metrics(query, autoscaler, metric, load_pattern)

    # Plot all metrics
    plot_experiments(query, autoscaler, metric, load_pattern)

    # Plot a subset of metrics
    plot_detailed_plot(query, autoscaler, metric, load_pattern, DETAILED_METRICS)

    # Calculate the evaluation metrics
    calulate_evaluation_metrics(query, autoscaler, metric, load_pattern)



