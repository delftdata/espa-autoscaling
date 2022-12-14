from MetricFetcher import MetricFetcher
from Configuration import Configurations

import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) >= 4:
        prometheus_address = arguments[0]
        experiment_length_minutes = int(arguments[1])
        data_step_size_seconds = int(arguments[2])
        main_directory: str = arguments[3]
        experiment_tag: str = arguments[4]

        mode = arguments[5]
        query = arguments[6]
        autoscaler: str = arguments[7]
        run_label = arguments[8]

        # default is non-reactive
        if mode == "non-reactive":
            mode = ""



        print(f"Processing data from {prometheus_ip} of {query} with {autoscaler}-{metric} on {load_pattern} ")
        process_data(prometheus_ip, query, autoscaler, load_pattern, metric, experiment_time_minutes)
    else:
        print(f"Unsufficient parameters. Expected: [prometheus_ip, query, autoscaler, metric, [load_pattern]]. Received: {arguments}")





     = "t1"


    experiment_query: str = "1"
    experiment_run_label: str = "4m"


    if experiment_run_label:
        experiment_run_label = f"[{experiment_run_label}]"

    data_directory = f"{main_directory}/{experiment_tag}"
    experiment_identifier = f"{experiment_run_label}q{experiment_query}_{experiment_autoscaler}"

    configs: Configurations = Configurations(
        data_directory,
        experiment_identifier,
        prometheus_address,
        experiment_length_minutes,
        data_step_size_seconds
    )
    metric_fetcher: MetricFetcher = MetricFetcher(configs)
    metric_fetcher.fetch_data()
