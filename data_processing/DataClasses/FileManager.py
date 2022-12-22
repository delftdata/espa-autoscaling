import os


class FileManager:

    @staticmethod
    def get_graph_folder(main_folder):
        return f"{main_folder}/graphs"

    @staticmethod
    def get_plot_folder(main_folder, plot_folder_name):
        graph_folder = FileManager.get_graph_folder(main_folder)
        return f"{graph_folder}/{plot_folder_name}"

    @staticmethod
    def get_data_folder(main_folder):
        return f"{main_folder}/data"

    @staticmethod
    def get_combined_data_folder(main_folder):
        data_folder = FileManager.get_data_folder(main_folder)
        return f"{data_folder}/combined_data"

    @staticmethod
    def get_files_in_folder(folder: str):
        """
        Get a list of all files in a specific folder.
        """
        files = os.listdir(folder)
        return files

    @staticmethod
    def get_all_files_and_paths_in_folder(folder: str):
        """
        Get a dictionary with as key the filename and as value the location of the file found in a folder.
        """
        files = FileManager.get_files_in_folder(folder)
        file_path_mapping = {}
        for file in files:
            file_path_mapping[file] = f"{folder}/{file}"
        return file_path_mapping

    @staticmethod
    def get_plot_filename(experiment_name, plot_postfix_label):
        plot_postfix_label = f"_{plot_postfix_label}" if plot_postfix_label else ""
        return f"{experiment_name}{plot_postfix_label}"
