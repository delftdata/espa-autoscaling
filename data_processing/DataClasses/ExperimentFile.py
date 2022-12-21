from Experiment import Experiment
import os
import os.path


class ExperimentFile:

    file_path: str
    experiment: Experiment

    def __init__(self, experiment: Experiment, file_path: str):
        self.experiment = experiment
        self.file_path = file_path
        if not self.fileExists(self.file_path):
            print(f"Error: File {file_path} of {self.experiment} does not exist.")

    def __str__(self):
        return f"ExperimentFile[{self.experiment}, {self.file_path}]"
    __repr__ = __str__

    @staticmethod
    def fileExists(file_path: str) -> bool:
        return os.path.isfile(file_path)

    def get_query(self):
        return self.experiment.get_query()

    def get_autoscaler(self):
        return self.experiment.get_autoscaler()

    def get_mode(self):
        return self.experiment.get_mode()

    def get_tag(self):
        return self.experiment.get_tag()

    def get_experiment_name(self):
        return self.experiment.get_experiment_name()
