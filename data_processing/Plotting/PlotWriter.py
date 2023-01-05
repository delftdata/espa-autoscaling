import os


def __ensure_directory_exists(directory):
    if not os.path.exists(directory):
        print(f"Creating directory {directory}")
        os.makedirs(directory)


def __get_file_location(save_directory, save_name, extension):
    return f"{save_directory}/{save_name}.{extension}"


def save_plot(plt, save_directory, save_name: str, extension="png"):
    save_directory = f"{save_directory}/{extension}" if extension != "png" else save_directory
    __ensure_directory_exists(save_directory)
    file_path = __get_file_location(save_directory, save_name, extension)
    plt.savefig(file_path, bbox_inches='tight')
    print(f"Successfully saved plot at {file_path}")


def show_plot(plt):
    plt.show()


def save_data(save_directory, save_name: str, data_string: str, extension="log"):
    __ensure_directory_exists(save_directory)
    file_path = __get_file_location(save_directory, save_name, extension)
    with open(file_path, 'w+', newline='') as f:
        f.write(data_string)
    print(f"Successfully saved data at {file_path}")

