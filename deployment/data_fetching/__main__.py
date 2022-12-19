from MetricFetcher import MetricFetcher
from Configuration import Configurations

import sys

"""
Main function of data fetching.
Expected inputs:
    * prometheus_ip: ip of prometheus server
    * prometheus_port: port of prometheus server
    * experiment_length-minutes: length of experiment in minutes. 
        When generating timestamps, data is fetched from [now - experiment_length, now].
        When providing timestamps, data is fetched from provided timestamps but filtered from [begin_timestamp, 
        begin_timestamp + experiment_length]
    * data_step_size_seconds: data_point step size from which data is fetched.
    * data_directory: directory where to store the data.
    * experiment_identifier: identifier of the experiment to fetch data for. Should be unique and will overwrite data of 
        experiment that already exists. 
    * timestamp_file [optional]: optional parameter that allows the user to provide self-defined timestamps. Timestamps
        should be in UTC timezone and is formatted inside the file in the following way: begin_timestamp,end_timestamp
"""
if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) >= 6:
        prometheus_ip = arguments[0]
        prometheus_port = arguments[1]
        experiment_length_minutes = int(arguments[2])
        data_step_size_seconds = int(arguments[3])
        data_directory: str = arguments[4]
        experiment_identifier: str = arguments[5]
        timestamp_file: str = ""
        if len(arguments) >= 7:
            timestamp_file: str = arguments[6]
            print(f"Found timestamp file: {timestamp_file}")

        print(f"Starting experiment with data_directory={data_directory} and "
              f"experiment_identifier={experiment_identifier}")
        configs: Configurations = Configurations(
            data_directory, experiment_identifier,
            prometheus_ip, prometheus_port,
            experiment_length_minutes, data_step_size_seconds
        )

        metric_fetcher: MetricFetcher = MetricFetcher(configs)
        metric_fetcher.fetch_data(timestamp_file)

    else:
        print(f"Insufficient parameters. Expected: [prometheus_ip, prometheus_port, experiment_length_minutes, "
              f"data_step_size_seconds, data_directory, experiment_identifier (timestamp_path)] Received: {arguments}")

