import pandas
from prometheus_api_client import MetricRangeDataFrame

from data_processing import Configurations


class PandasManager:
    configs: Configurations

    def __init__(self, configurations: Configurations):
        self.configs = configurations

    def write_individual_metric_data_to_file(self, metric, metric_df):
        filePath = self.configs.get_individual_metric_data_path(metric)
        metric_df.to_csv(filePath)

    def combine_all_individual_metric_files(self):
        known_individual_metric_file_paths: [str] = self.configs.get_known_individual_files()

        combined_data = pandas.read_csv(known_individual_metric_file_paths.pop())
        combined_data["datetime"] = pandas.to_datetime(combined_data['timestamp'], format="%Y/%m/%d")
        # set timestampe


        input_data = pd.read_csv(path_to_files + "input_rate.csv")

        # convert timestamps to seconds

        # remove first files of experiment
        input_data = input_data.loc[input_data['value'] != 0]

        # get number of minutes and seconds since start of experiment
        input_data = input_data.reset_index()
        input_data['seconds'] = input_data.index.values * 15
        input_data['minutes'] = input_data.index.values * 0.25

        # filter tail of dataframe
        input_data = input_data.loc[input_data['minutes'] <= 140]

        # remove column
        input_data = input_data.drop(labels="__name__", axis="columns")

        # rename 'value' to metric name
        input_data = input_data.rename(columns={"value": "input_rate"})

        for metric in metrics:
            df = pd.read_csv(path_to_files + metric + ".csv")
            df = df.drop(labels="__name__", axis="columns")
            df = df.rename(columns={"value": metric})
            input_data = input_data.join(df.set_index('timestamp'), on="timestamp", how='left')

        metrics = ["input_rate", "backpressure", "busy_time", "CPU_load", "idle_time", "lag", "latency", "taskmanager",
                   "throughput"]

        for metric in metrics:
            input_data[metric] = input_data[metric].interpolate()

        input_data = input_data.fillna(0)

        path = "./experiment_data/full_data/" + load_pattern + "/" + query
        if not os.path.exists(path):
            os.makedirs(path)
        input_data.to_csv(path + "/" + query + "_" + auto_scaler + "_" + percentage + ".csv")

