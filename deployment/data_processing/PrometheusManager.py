import dateparser

from Configuration import Configurations

from datetime import datetime
import prometheus_api_client
import prometheus_api_client.utils
from prometheus_api_client import PrometheusConnect


class PrometheusManager:
    configs: Configurations
    prometheus_connection: PrometheusConnect

    def __init__(self, configurations: Configurations):
        self.configs = configurations
        self.prometheus_connection = PrometheusConnect(url=f"http://{self.configs.prometheus_ip}:"
                                                           f"{self.configs.prometheus_port}",
                                                       disable_ssl=True)

    def get_prometheus_experiment_start_and_end_datetime(self):
        # Get timestamp in UTC
        start_datetime = dateparser.parse(f"{self.configs.experiment_length_minutes}m", settings={'TIMEZONE': 'UTC'})
        end_datetime = dateparser.parse(f"now", settings={'TIMEZONE': 'UTC'})

        # Explicitly state timesone in timestamp
        start_datetime_UTC = dateparser.parse(f"{start_datetime} UTC")
        end_datetime_UTC = dateparser.parse(f"{end_datetime} UTC")

        # Return datetimes
        return start_datetime_UTC, end_datetime_UTC

    def fetch_data_from_prometheus(self, query, start_datetime=None, end_datetime=None):
        if not start_datetime or not end_datetime:
            tmp_start_datetime, tmp_end_datetime = self.get_prometheus_experiment_start_and_end_datetime()
            start_datetime = tmp_start_datetime if not start_datetime else start_datetime
            end_datetime = tmp_end_datetime if not end_datetime else end_datetime

        prometheus_data = self.prometheus_connection.custom_query_range(
            query=query,
            start_time=start_datetime,
            end_time=end_datetime,
            step=f"{self.configs.data_step_size_seconds}s",
        )
        return prometheus_data

    def get_pandas_dataframe_from_prometheus(self, query, start_timestamp=None, end_timestamp=None):
        prometheus_data = self.fetch_data_from_prometheus(query, start_timestamp, end_timestamp)
        metric_data = prometheus_api_client.MetricRangeDataFrame(prometheus_data)
        return metric_data
