import os


class Configurations:
    data_directory: str

    prometheus_address: str
    prometheus_port: int = 9090

    experiment_length_minutes: int
    data_step_size_seconds: int

    known_individual_files: [str] = []

    def __init__(self, data_directory: str, prometheus_address: str, experiment_length_minutes: int,
                 data_step_size_seconds: int):
        self.prometheus_address = prometheus_address
        self.data_directory = data_directory
        self.initialize_directories()
        self.experiment_length_minutes = experiment_length_minutes
        self.data_step_size_seconds = data_step_size_seconds

    def initialize_directories(self):
        directories = [self.get_individual_data_directory(), self.get_combined_data_directory()]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def get_known_individual_files(self):
        return self.known_individual_files

    def get_individual_data_directory(self):
        individualDataDirectory = f"{self.data_directory}/individualData"
        return individualDataDirectory

    def get_combined_data_directory(self):
        combinedDataDirectory = f"{self.data_directory}/individualData"
        return combinedDataDirectory

    def get_individual_metric_data_path(self, metric: str):
        filePath = self.get_individual_data_directory() + f"/{metric}.csv"
        self.known_individual_files.append(filePath)
        return filePath


