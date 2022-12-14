import pandas
import pandas.core.api
import math
from Configuration import Configurations


class PandasManager:
    configs: Configurations

    def __init__(self, configurations: Configurations):
        self.configs = configurations

    def write_combined_metrics_data_to_file(self, combined_metrics_df):
        filePath = self.configs.get_combined_metric_data_path()
        self.write_dataframe_to_file(filePath, combined_metrics_df)

    def write_individual_metric_data_to_file(self, metric_name, metric_df):
        filePath = self.configs.get_individual_metric_data_path(metric_name)
        self.write_dataframe_to_file(filePath, metric_df)

    @staticmethod
    def write_dataframe_to_file(filePath, dataframe):
        dataframe.to_csv(filePath)

    def combine_individual_metrics_and_write_to_file(self):
        combined_data = None
        for metric_name, data_path in self.configs.get_known_individual_data_files().items():
            # Read data
            metric_data = pandas.read_csv(data_path)
            # Drop __name__ column
            metric_data = metric_data.drop(labels="__name__", axis="columns")
            # Rename values column to metric_name
            metric_data = metric_data.rename(columns={"value": metric_name})

            if combined_data is None:
                # Convert timestamps to seconds
                metric_data["datetime"] = pandas.to_datetime(metric_data['timestamp'], format="%Y/%m/%d")

                # Remove first line of experiment
                metric_data = metric_data.loc[metric_data[metric_name] != 0]

                # get number of minutes and seconds since start of experiment
                metric_data = metric_data.reset_index()
                metric_data['seconds'] = metric_data.index.values * self.configs.data_step_size_seconds
                metric_data['minutes'] = metric_data.index.values * (60 / self.configs.data_step_size_seconds)

                # Remove data from outside experiment period
                metric_data = metric_data.loc[metric_data['minutes'] <= self.configs.experiment_length_minutes]

                # Assign metric_Data to combined_data
                combined_data = metric_data
            else:
                # Join data with combined_data on timestamp
                combined_data = combined_data.join(metric_data.set_index('timestamp'), on="timestamp", how='left')

        # Interpolate missing metrics
        for metric_name in self.configs.get_known_individual_data_files().keys():
            combined_data[metric_name] = combined_data[metric_name].interpolate()

        # Replace NaN data with 0
        combined_data = combined_data.fillna(0)

        # Write data to file
        self.write_combined_metrics_data_to_file(combined_data)


