import dateparser

from Configuration import Configurations
import os


class FileWriter:
    configs: Configurations

    def __init__(self, configurations: Configurations):
        """
        Constructor of FileWriter
        """
        self.configs = configurations

    def initialize_known_directories(self):
        """
        Initialize all known directories. All known directories are generally all directories in which data is saved.
        """
        directories: [str] = self.configs.get_known_directories()
        self.initialize_directories(directories)

    def initialize_directories(self, directories: [str]):
        """
        Initialize a list of directories.
        """
        for directory in directories:
            self.initialize_directory(directory)

    @staticmethod
    def initialize_directory(directory: str):
        """
        Initialize a single directory
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_start_end_time_to_file(self, start_timedate, end_timedate):
        """
        Write the start_datetime and end_datetime of the current experiment to a file.
        The datetimes are saved in the following format "{start_datetime},{end_datetime} and are in ETC Time.
        """
        start_end_datetime_path = self.configs.get_start_end_datetime_path()

        with open(start_end_datetime_path, 'w', newline='') as f:
            f.write(f"{start_timedate},{end_timedate}")
        print(f"Written experiment timestamps to {start_end_datetime_path}")

    @staticmethod
    def read_start_end_time_from_file(timedate_file_path):
        """
        Read the start_datetime and end_datetime from a file.
        The datetime's should be formatted in the following way: "{start_datetime},{end_datetime} and are in ETC Time.
        """
        with open(timedate_file_path, 'r', newline='') as f:
            timedates = f.read()
            split_timedates = timedates.split(",")
            if len(split_timedates) == 2:
                start_timedate = dateparser.parse(split_timedates[0])
                end_timedate = dateparser.parse(split_timedates[1])
                return start_timedate, end_timedate
            else:
                raise Exception(f"Timedate format of {timedate_file_path} is invalid.")
