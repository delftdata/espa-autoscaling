from .Autoscalers import Autoscalers
from .Queries import Queries
from .Modes import Modes


class Experiment:
    __query: str
    __autoscaler: str
    __mode: str
    __tag: str

    def __init__(self, query: str, autoscaler: str, mode: str, tag: str = None):
        self.__query = query
        self.__autoscaler = autoscaler
        self.__mode = mode
        self.__tag = tag if tag else ""
        if not Experiment.is_valid_experiment(self):
            print(f"Error constructing experiment: {self} is not a valid experiment!")

    def __str__(self):
        return f"Experiment[{self.get_experiment_name()}]"

    __repr__ = __str__

    def get_tag(self):
        """
        Get the tag of the experiment
        """
        return self.__tag

    def get_query(self):
        """
        Get the query of the experiment
        """
        return self.__query

    def get_autoscaler(self):
        """
        Get the autoscaler of the experiment
        """
        return self.__autoscaler

    def get_mode(self):
        """
        Get the mode of the experiment.
        """
        return self.__mode

    def get_experiment_name(self):
        """
        Get the full name of the experiment
        """
        return Experiment.get_experiment_name_from_data(self.get_query(), self.get_autoscaler(), self.get_mode(),
                                                        self.get_tag())

    def is_similar_experiment(self, other, ignore_query=False, ignore_autoscaler=False, ignore_autoscaler_config=False, ignore_mode=False,
                              ignore_tag=False):
        """
        Check whether other is a similar experiment as this one.
        If ignoreTag is set to True, the tag is not compared.
        """
        if type(other) == Experiment:
            is_similar = True
            is_similar = is_similar and (ignore_query or self.get_query() == other.get_query())
            is_similar = is_similar and (ignore_autoscaler or Autoscalers.get_autoscaler_class(self.get_autoscaler()) ==
                                         Autoscalers.get_autoscaler_class(other.get_autoscaler()))
            is_similar = is_similar and (ignore_autoscaler_config or (Autoscalers.get_auto_scaler_label(self.get_autoscaler()) ==
                                                                      Autoscalers.get_auto_scaler_label(other.get_autoscaler())))
            is_similar = is_similar and (ignore_mode or self.get_mode() == other.get_mode())
            is_similar = is_similar and (ignore_tag or self.get_tag() == other.get_tag())


            return is_similar
        return False

    @staticmethod
    def is_valid_experiment(experiment):
        """
        Function checking whether the provided experiment is a valid experiment.
        """
        return Experiment.is_valid_experiment_data(experiment.get_query(), experiment.get_autoscaler(),
                                                   experiment.get_mode(), experiment.get_tag())

    @staticmethod
    def is_valid_experiment_data(query: str, autoscaler: str, mode: str, tag: str = None) -> bool:
        """
        Function checking whether the provided data combination would be a valid experiment.
        """
        autoscaler_main_name = autoscaler.split("(")[0]
        query_main_name = query.split("(")[0]
        # Any tag is supported
        return (
                Queries.is_query(query_main_name) and
                Autoscalers.is_autoscaler(autoscaler_main_name) and
                Modes.is_mode(mode)
        )

    @staticmethod
    def get_experiment_name_from_data(query: str, autoscaler: str, mode: str, tag: str = None):
        """
        Get the full experiment name from the provided data
        """
        tag = f"[{tag}]" if tag else ""
        mode = f"_{mode}" if mode else ""
        experiment_name = f"{tag}q{query}_{autoscaler}{mode}"
        return experiment_name

    @staticmethod
    def get_experiment_name_from_data_leave_missing_data_out(query: str, autoscaler: str, mode: str, tag: str = None):
        """
        Get experiment_name from the provided data. If data is not provided out, it is used in the name.
        :param query: Query of the experiment
        :param autoscaler: Autoscaler of the experiment
        :param mode: Mode of the experiment
        :param tag: Tag of the experiment
        :return:
        """
        result = ""
        if tag:
            result = f"[{tag}]"

        items = []
        if query:
            items.append(f"q{query}")
        if autoscaler:
            items.append(f"{autoscaler}")
        if mode:
            items.append(f"{mode}")

        for item in items:
            result = f"{result}_" if result else ""
            if item:
                result = f"{result}{item}"
        return result


    @staticmethod
    def get_experiment_class_from_experiment_name(experiment_name: str):
        """
        Provided an experiment_name, create an experiment class from it.
        Returns None if the name is invalid
        """
        # if name contains ']"
        if "]" in experiment_name:
            # contains tag
            tag_split = experiment_name.replace("[", "").split("]")
            if len(tag_split) == 2:
                tag = tag_split[0]
                experiment_name = tag_split[1]
            else:
                print(f"Error: wrong amount of tag_split information present information present in experiment_name "
                      f"'{experiment_name}': '{tag_split}'. Returning None.")
                return None
        else:
            tag = ""

        data_points = experiment_name.split("_")
        if len(data_points) < 2:
            print(
                f"Error: not enough information can be subtracted from experiment_name '{experiment_name}. Returning None")
            return None

        query = data_points.pop(0).replace("q", "")
        autoscaler = data_points.pop(0)
        mode = data_points.pop(0) if len(data_points) >= 2 else ""

        if len(data_points) > 0:
            print(
                f"Warning: after parsing experiment_name '{experiment_name}', the following datapoints remain: {data_points}")

        experiment: Experiment = Experiment(query, autoscaler, mode, tag)
        if Experiment.is_valid_experiment(experiment):
            return experiment
        else:
            print(
                f"Error: the generated experiment {experiment} from experiment_name {experiment} is invalid. Returning None.")
            return None
