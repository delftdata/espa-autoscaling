from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
from data_processing import Configurations


class DataScraper:
    configs: Configurations
    prometheus_connection: PrometheusConnect

    def __init__(self, configurations: Configurations):
        self.configs = configurations
        self.prometheus_connection = PrometheusConnect(url=f"http://{self.configs.prometheus_address}:"
                                                           f"{self.configs.prometheus_port}",
                                                       disable_ssl=True)

    def fetch_data_from_prometheus(self, query):
        metric_data = self.prometheus_connection.custom_query_range(
            query=query,
            start_time=parse_datetime(f"{self.configs.experiment_length_minutes}m"),
            end_time=parse_datetime("now"),
            step=f"{self.configs.data_step_size_seconds}s",
        )
        return metric_data

    def get_pandas_dataframe_from_prometheus(self, metric_name, query):
        prometheus_data = self.fetch_data_from_prometheus(query)
        metric_data = prometheus_data[0]['metric'] = {'__name__': metric_name}
        metric_df = MetricRangeDataFrame(metric_data)
        return metric_df
