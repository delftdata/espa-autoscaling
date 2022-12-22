from Queries import Queries
from Autoscalers import Autoscalers
from Modes import Modes
from Experiment import Experiment
from ExperimentFile import ExperimentFile
from FileManager import FileManager


class ExperimentFileGenerator:

    @staticmethod
    def get_all_experiment_files_from_main_folder(main_folder):
        """
        Get a list of ExperimentFile classes from the combined data folder in the provided main_folder.
        All provided ExperimentFile classes contain a valid experiment configuration.
        """
        combined_data_folder = FileManager.get_combined_data_folder(main_folder)
        return ExperimentFileGenerator.get_all_experiment_files_from_combined_data_folder(combined_data_folder)

    @staticmethod
    def get_specific_experiment_files_from_main_folder(main_folder: str,
                                                       selected_queries=None, selected_autoscalers=None,
                                                       selected_modes=None, selected_tags=None):
        """
        Get a list of ExperimentFiles from the combined data folder in the provided main_folder. The method will ensure
        only selected queries, autoscalers, modes or tags are contained in the list. When a selected configuration is
        not provided, all known configurations are supported.
        """
        combined_data_folder = FileManager.get_combined_data_folder(main_folder)
        return ExperimentFileGenerator.get_specific_experiment_files_from_combined_data_folder(
            combined_data_folder, selected_queries, selected_autoscalers, selected_modes, selected_tags)

    @staticmethod
    def get_all_experiment_files_from_combined_data_folder(combined_data_folder):
        """
        Get a list of ExperimentFile classes from a combined_data_folder folder. All provided ExperimentFile classes
        contain a valid experiment configuration.
        """
        combined_data_folder = FileManager.get_combined_data_folder(combined_data_folder)
        file_path_mapping = FileManager.get_all_files_and_paths_in_folder(combined_data_folder)
        experiment_files = []
        for experiment, experiment_path in file_path_mapping.items():
            experiment_name = experiment.replace("_data.csv", "")
            experiment_class = Experiment.get_experiment_class_from_experiment_name(experiment_name)
            if experiment_class:
                experiment_file = ExperimentFile(experiment_class, experiment_path)
                experiment_files.append(experiment_file)
        return experiment_files

    @staticmethod
    def get_specific_experiment_files_from_combined_data_folder(combined_data_folder: str,
                                                                selected_queries=None, selected_autoscalers=None,
                                                                selected_modes=None, selected_tags=None):
        """
        Get a list of ExperimentFiles from a specific folder and ensure only selected queries, autoscalers, modes or
        tags are contained in the list. When a selected configuration is not provided, all known configurations are
        supported.
        """
        selected_queries = selected_queries or Queries.get_all_queries()
        selected_autoscalers = selected_autoscalers or Autoscalers.get_all_autoscalers()
        selected_modes = selected_modes or Modes.get_all_modes()

        all_experiment_files: [ExperimentFile] = ExperimentFileGenerator.\
            get_all_experiment_files_from_combined_data_folder(combined_data_folder)
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


    @staticmethod
    def fastCombineSimilarExperiments(experimentFiles: [ExperimentFile], ignoreLabel=True):
        """
        Function combines all similar experiments in a single list.
        :param experimentFiles: ExperimentFiles to combine all similar experiments
        :param ignoreLabel: Whether to ignor ethe label recognizing simmilar experiments
        :return: List of lists containing all similar experiments
        """
        combinations = []
        for experimentFile in experimentFiles:
            found = False
            for combination in combinations:
                if experimentFile.experiment.isSimilarExperiment(combination[0].experiment, ignoreLabel=ignoreLabel):
                    combination.append(experimentFile)
                    found = True
                    break
            if not found:
                combinations.append([experimentFile])
        return combinations

    @staticmethod
    def deleteTooSmallLists(experimentFiles: [[ExperimentFile]], minimumSize: int):
        return list(filter(lambda l: len(l) >= minimumSize, experimentFiles))