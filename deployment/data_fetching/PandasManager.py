import pandas
import pandas.core.api
from Configuration import Configurations


class PandasManager:
    configs: Configurations

    def __init__(self, configurations: Configurations):
        """
        Constructor of the PandasManager
        """
        self.configs = configurations

    def write_combined_metrics_data_to_file(self, combined_metrics_df):
        """
        Write a dataframe to the get_combined_metric_data_path.
        The dataframe meant to contain all data collected from the experiment.
        """
        filePath = self.configs.get_combined_metric_data_path()
        self.write_dataframe_to_file(filePath, combined_metrics_df)
        print(f"Combined metrics and saved them at {filePath}")

    def write_individual_metric_data_to_file(self, metric_name, metric_df):
        """
        Write the result of a single_column_query with name {metric_name} to file.
        """
        filePath = self.configs.get_individual_metric_data_path(metric_name)
        self.write_dataframe_to_file(filePath, metric_df)

    def write_task_specific_metric_data_to_file(self, metric_name, metric_data):
        """
        Write the results of a task_specific_metric_data_frame to file.
        The dataframe is first split per task_name and written to a single file named {metric_name}_{task_name}.
        """
        task_names = metric_data["task_name"].unique()
        for task_name in task_names:
            metric_task_name = f"{metric_name}-{task_name}"
            metric_task_data = metric_data[metric_data['task_name'] == task_name]
            metric_task_data = metric_task_data.drop(labels="task_name", axis="columns")
            self.write_individual_metric_data_to_file(metric_task_name, metric_task_data)

    @staticmethod
    def write_dataframe_to_file(filePath, dataframe):
        """
        Write a panda's dataframe to file.
        Filepath: path where to save the data-frame
        Data-frame: dataframe to save to file.
        """
        dataframe.to_csv(filePath)

    def combine_individual_metrics_and_write_to_file(self):
        """
        Combine all known individual metric datafiles into a single datafile.
        """
        combined_data = None
        for metric_name, data_path in self.configs.get_known_individual_data_files().items():
            # Read data
            metric_data = pandas.read_csv(data_path)
            # Rename values column to metric_name
            metric_data = metric_data.rename(columns={"value": metric_name})

            if combined_data is None:
                print(f"First metric: {metric_name}")

                # Remove first line of experiment
                metric_data = metric_data.loc[metric_data[metric_name] != 0]

                # Assign metric_Data to combined_data
                combined_data = metric_data
            else:
                # Join data with combined_data on timestamp
                combined_data = combined_data.join(metric_data.set_index('timestamp'), on="timestamp", how='outer')


        # Reset index of experiment and remove old index
        combined_data = combined_data.reset_index()
        combined_data = combined_data.drop(labels="index", axis=1)

        # Get number of minutes and seconds since start of experiment
        combined_data.insert(1, "datetime", pandas.to_datetime(combined_data['timestamp'], format="%Y/%m/%d"))
        combined_data.insert(2, "seconds", combined_data.index.values * self.configs.data_step_size_seconds)
        combined_data.insert(3, "minutes", combined_data.index.values * (self.configs.data_step_size_seconds / 60))

        # Remove data from outside experiment period. Experiment runs from [begin-time, begin-time + experiment_length]
        combined_data = combined_data.loc[combined_data['minutes'] <= self.configs.experiment_length_minutes]

        # Interpolate missing metrics
        if self.configs.COMBINED_DATA_INTERPOLATE:
            for metric_name in self.configs.get_known_individual_data_files().keys():
                combined_data[metric_name] = combined_data[metric_name].interpolate()

        # Replace NaN data with 0
        if self.configs.COMBINED_DATA_FILL_NAN_WITH_ZERO:
            combined_data = combined_data.fillna(0)

        # Write data to file
        self.write_combined_metrics_data_to_file(combined_data)


