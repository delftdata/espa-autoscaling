class Configurations:
    # Whether to interpolate missing data in the combined data file
    COMBINED_DATA_INTERPOLATE = False
    # Whether to fill missing data (NaN) values with zero's in the combined data file
    COMBINED_DATA_FILL_NAN_WITH_ZERO = False

    # Directory where to save the data
    data_directory: str
    # Unique identifier of the experiment. Files of experiments with the same identifier will be overwritten
    experiment_identifier: str

    # IP of the prometheus server
    prometheus_ip: str
    # Port where the prometheus server can be accessed (generally 9090)
    prometheus_port: int

    # Length of the experiment. A currently running experiment is fetched from [now - experiment_length_minutes, now].
    # Data in the combined experiments is cut of after {experiment_length_minutes}
    experiment_length_minutes: int
    # Data step size seconds of data that has to be fetched (preferably similar to Prometheus's fetching period)
    data_step_size_seconds: int

    # List of directories where data is written by the data_fetcher
    known_directories: [str] = []
    # List of files containing data of single (individual) metrics where data is writen
    known_individual_data_files: {str, str} = {}

    def __init__(self, data_directory: str, experiment_identifier: str,
                 prometheus_ip: str, prometheus_port,
                 experiment_length_minutes: int, data_step_size_seconds: int):
        """
        Constructor of the configuration class.
        """
        self.data_directory = data_directory
        self.experiment_identifier = experiment_identifier

        self.prometheus_ip = prometheus_ip
        self.prometheus_port = prometheus_port

        self.experiment_length_minutes = experiment_length_minutes
        self.data_step_size_seconds = data_step_size_seconds

        self.known_directories.append(self.get_individual_data_directory())
        self.known_directories.append(self.get_combined_data_directory())
        self.known_directories.append(self.get_start_end_datetime_directory())


    @staticmethod
    def convertFileNameToSupportedName(operatorName: str):
        """
        The operator names of Prometheus differ from the Jobmanager. While the jobmanager supports " ", ".", and "-",
        Prometheus presents the characters as a "_". To ensure compatibility between the prometheus metrics and the
        jobmanager metrics, characters in the operator names are replaced with "_".
        :param operatorName: Operatorname to replace characters with.
        :return: Operator name that has all forbidden characters replaced with a "_"
        """
        unsupportedCharacters = ["-&gt", " ", "-", ":", ";", ">", "<"]
        for unsupportedCharacter in unsupportedCharacters:
            operatorName = operatorName.replace(unsupportedCharacter, "_")
        return operatorName

    def get_known_directories(self):
        """
        Get a list of all known directories in which files are saved.
        """
        return self.known_directories

    def get_known_individual_data_files(self):
        """
        Get a list of all known datafiles containing the data of a single (individual) metric
        """
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
        metric_name = self.convertFileNameToSupportedName(metric_name)
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
        filePath = f"{self.get_combined_data_directory()}/{self.experiment_identifier}_data.csv"
        return filePath







