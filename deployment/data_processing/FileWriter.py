from Configuration import Configurations
import os


class FileWriter:

    configs: Configurations

    def __init__(self, configurations: Configurations):
        self.configs = configurations

    def initialize_known_directories(self):
        directories: [str] = self.configs.get_known_directories()
        self.initialize_directories(directories)

    def initialize_directories(self, directories: [str]):
        for directory in directories:
            self.initialize_directory(directory)

    @staticmethod
    def initialize_directory(directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_start_end_time_to_file(self, start_timedate, end_timedate):
        start_end_datetime_path = self.configs.get_start_end_datetime_path()

        with open(start_end_datetime_path, 'w', newline='') as f:
            f.write(f"{start_timedate},{end_timedate}")
