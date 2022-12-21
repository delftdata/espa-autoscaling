from Queries import Queries
from Autoscalers import Autoscalers
from Modes import Modes


from Experiment import Experiment
from ExperimentFile import ExperimentFile
import os
import sys


class ExperimentFileGenerator:
    main_folder: str
    graph_folder: str
    data_folder: str
    combined_data_folder: str


    def __init__(self, main_folder: str):
        self.main_folder = main_folder
        self.graph_folder = f"{main_folder}/graphs"
        self.data_folder = f"{main_folder}/data"
        self.combined_data_folder = f"{main_folder}/data/combined_data"

    def get_files_in_folder(self, folder: str):
        """
        Get a list of all files in a specific folder.
        """
        files = os.listdir(folder)
        return files

    def get_all_files_and_paths_in_folder(self, folder: str):
        """
        Get a dictionary with as key the filename and as value the location of the file found in a folder.
        """
        files = self.get_files_in_folder(folder)
        file_path_mapping = {}
        for file in files:
            file_path_mapping[file] = f"{folder}/{file}"
        return file_path_mapping

    def get_all_experiment_files_from_folder(self, folder):
        """
        Get a list of ExperimentFile classes from a specific folder. All provided ExperimentFile classes contain a valid
        experiment configuration.
        """
        file_path_mapping = self.get_all_files_and_paths_in_folder(folder)
        experiment_files = []
        for experiment, experiment_path in file_path_mapping.items():
            experiment_name = experiment.replace("_data.csv", "")
            experiment_class = Experiment.get_experiment_class_from_experiment_name(experiment_name)
            if experiment_class:
                experiment_file = ExperimentFile(experiment_class, experiment_path)
                experiment_files.append(experiment_file)
        return experiment_files

    def get_specific_experiment_files_from_folder(self, folder: str, selected_queries=None, selected_autoscalers=None,
                                                  selected_modes=None, selected_tags=None):
        """
        Get a list of ExperimentFiles from a specific folder and ensure only selected queries, autoscalers, modes or
        tags are contained in the list. When a selected configuration is not provided, all known configurations are
        supported.
        """
        selected_queries = selected_queries or Queries.getAllQueries()
        selected_autoscalers = selected_autoscalers or Autoscalers.getAllAutoscalers()
        selected_modes = selected_modes or Modes.getAllModes()

        all_experiment_files: [ExperimentFile] = self.get_all_experiment_files_from_folder(folder)
        filtered_experiment_files = []
        for experiment_file in all_experiment_files:
            if (
                    experiment_file.get_query() in selected_queries
                    and experiment_file.get_autoscaler() in selected_autoscalers
                    and experiment_file.get_mode() in selected_modes
                    and (not selected_tags or experiment_file.get_tag() in selected_tags)
            ):
                filtered_experiment_files.append(experiment_file)
        return filtered_experiment_files


if __name__ == "__main__":
    # Temporary main function for testing the application
    arguments = sys.argv[1:]
    fileGenerator = ExperimentFileGenerator(arguments[0])
    print(fileGenerator.get_specific_experiment_files_from_folder(
        fileGenerator.combined_data_folder,
        selected_tags=["rerun", "c5m"]
    ))
