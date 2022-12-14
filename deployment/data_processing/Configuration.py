class Configurations:
    data_directory: str
    experiment_identifier: str

    prometheus_address: str
    prometheus_port: int = 9090

    experiment_length_minutes: int
    data_step_size_seconds: int

    known_directories: [str] = []

    known_individual_data_files: {str, str} = {}

    def __init__(self, data_directory: str, experiment_identifier: str,
                 prometheus_address: str, experiment_length_minutes: int,
                 data_step_size_seconds: int):
        self.prometheus_address = prometheus_address
        self.data_directory = data_directory
        self.experiment_identifier = experiment_identifier
        self.experiment_length_minutes = experiment_length_minutes
        self.data_step_size_seconds = data_step_size_seconds

        self.known_directories.append(self.get_individual_data_directory())
        self.known_directories.append(self.get_combined_data_directory())
        self.known_directories.append(self.get_start_end_datetime_directory())

    def get_known_directories(self):
        return self.known_directories

    def get_known_individual_data_files(self):
        return self.known_individual_data_files

    def get_start_end_datetime_directory(self):
        """
        Directory: {data_directory}/experiment_timestamps/
        """
        start_end_directory = f"{self.data_directory}/experiment_timestamps"
        return start_end_directory

    def get_start_end_datetime_path(self):
        """
        Directory: {data_directory}/experiment_timestamps/
        FileName: {experiment_identifier}_timestamps.csv
        Path:  {data_directory}/experiment_timestamps/{experiment_identifier}_timestamps.csv
        """
        filePath = f"{self.get_start_end_datetime_directory()}/{self.experiment_identifier}_timestamps.csv"
        return filePath

    def get_individual_data_directory(self):
        """
        Directory: {data_directory}/individual_data/{experiment_identifier}
        """
        individual_data_directory = f"{self.data_directory}/individual_data/{self.experiment_identifier}"
        return individual_data_directory

    def get_individual_metric_data_path(self, metric_name: str):
        """
        Directory: {data_directory}/individual_data/{experiment_identifier}
        FileName: {metric_name}.csv
        Path: {data_directory}/individual_data/{experiment_identifier}/{metric_name}.csv
        """
        filePath = f"{self.get_individual_data_directory()}/{metric_name}.csv"
        self.known_individual_data_files[metric_name] = filePath
        return filePath

    def get_combined_data_directory(self):
        """
        Directory: {data_directory}/combined_data
        """
        combined_data_directory = f"{self.data_directory}/combined_data"
        return combined_data_directory

    def get_combined_metric_data_path(self):
        """
        Directory: {data_directory}/combined_data
        FileName: {experiment_identifier}_data.csv
        Path: {data_directory}/combined_data/{experiment_identifier}_data.csv
        """
        combined_data_file_name = "combined_data"
        filePath = f"{self.get_combined_data_directory()}/{self.experiment_identifier}_data.csv"
        return filePath







