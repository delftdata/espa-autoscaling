from MetricFetcher import MetricFetcher
from Configuration import Configurations

import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) >= 5:
        prometheus_ip = arguments[0]
        prometheus_port = arguments[1]
        experiment_length_minutes = int(arguments[2])
        data_step_size_seconds = int(arguments[3])
        data_directory: str = arguments[4]
        experiment_identifier: str = arguments[5]

        print(f"Starting experiment with data_directory={data_directory} and "
              f"experiment_identifier={experiment_identifier}")
        configs: Configurations = Configurations(
            data_directory, experiment_identifier,
            prometheus_ip, prometheus_port,
            experiment_length_minutes, data_step_size_seconds
        )

        metric_fetcher: MetricFetcher = MetricFetcher(configs)
        metric_fetcher.fetch_data()

    else:
        print(f"Insufficient parameters. Expected: [prometheus_address] Received: {arguments}")

    experiment_query: str = "1"
    experiment_run_label: str = "4m"


    if experiment_run_label:
        experiment_run_label = f"[{experiment_run_label}]"



