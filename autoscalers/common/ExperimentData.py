class ExperimentData:
    operator_to_topic_naming = {
        "bidssource": "bids_topic",
        "auctionsource": "auction_topic",
        "auctionssource": "auction_topic",
        "personsource": "person_topic"
    }

    operator_to_parallelism_mapping = {
        # Sources
        "BidsSource": "--p-bids-source",
        "Source: BidsSource": "--p-bids-source",
        "Source: BidsSource -> BidsTimestampAssigner": "--p-bids-source",

        "AuctionSource": "--p-auction-source",
        "AuctionsSource": "--p-auction-source",
        "Source: auctionSource": "--p-auction-source",
        "Source: auctionsSource": "--p-auction-source",
        "Source: auctionsSource -> auctionsSource -> Map": "--p-auction-source",

        "PersonSource": "--p-person-source",
        "Source: personSource": "--p-person-source",
        "Source: personSource -> PersonTimestampAssigner -> Map": "--p-person-source",

        # Query 1
        "Mapper": "--p-map",
        # Query 2
        "Flatmap": "--p-flatMap",
        # Query 3
        "PersonFilter": "--p-filter",
        "IncrementalJoin": "--p-join",
        # Query 5
        "WindowCount": "--p-window",
        # Query 8
        "Window(TumblingEventTimeWindows(10000), EventTimeTrigger, CoGroupWindowFunction)": "--p-window",
        # Query 11
        "SessionWindow": "--p-window",

        # Sinks
        "LatencySink": "--p-sink",
    }

    def __init__(self):
        new_operator_to_parallelism_mapping = dict(self.operator_to_parallelism_mapping)
        for operator_name, parameter in self.operator_to_parallelism_mapping.items():
            stripped_operator_name = self.convert_operator_name_to_prometheus_operator_name(operator_name)
            new_operator_to_parallelism_mapping[stripped_operator_name] = parameter
        self.operator_to_parallelism_mapping = new_operator_to_parallelism_mapping

    @staticmethod
    def convert_operator_name_to_prometheus_operator_name(operator_name: str) -> str:
        """
        The operator names of Prometheus differ from the Jobmanager. While the jobmanager supports " ", ".", and "-",
        Prometheus presents the characters as a "_". To ensure compatibility between the prometheus metrics and the
        jobmanager metrics, characters in the operator names are replaced with "_".
        :param operator_name: Operatorname to replace characters with.
        :return: Operator name that has all forbidden characters replaced with a "_"
        """
        unsupported_characters = ["-&gt", " ", ",", ".", "-", ";", "/", ">", "(", ")"]
        for unsupported_character in unsupported_characters:
            operator_name = operator_name.replace(unsupported_character, "_")
        return operator_name


    def __subtract_source_name_from_operator_name(self, operator_name: str, print_error=True) -> str:
        """
        For all sourceNames in self.operator_to_topic_naming, check whether the sourceName is contained in operatorName
        and return the sourceName
        """
        for source_name in self.operator_to_topic_naming.keys():
            if source_name in operator_name.lower():
                return source_name
        if print_error:
            print(f"Error: could not determine sourceName from operatorName '{operator_name}'")

    def operator_is_a_source(self, operator_name: str) -> bool:
        """
        Determine whether operatorName is a source.
        """
        return self.__subtract_source_name_from_operator_name(operator_name, print_error=False) is not None

    def get_topic_from_operator_name(self, operator_name, print_error=True) -> str:
        """
        Given the name of an operator, return the topic the operator is a source for. If the operator is not found in
        operator_to_topic_mapping, nothing is returned.
        :param operator_name: Name of the operator to find the corresponding topic for
        :param print_error: Whether to print an error if not found
        :return: None or the topic a source operator is producing.
        """
        source_name = self.__subtract_source_name_from_operator_name(operator_name, print_error=False)
        if source_name in self.operator_to_topic_naming:
            return self.operator_to_topic_naming[source_name]
        else:
            if print_error:
                print(f"Error: could not fetch topic from operatorName '{operator_name}'")

    def get_parallelism_parameter_of_operator(self, operator, print_error: bool = True) -> str:
        """
        Get the parallelism parameter of the queries' Flink implementation to adjust the parallelism of the operator in the new jobmanager.
        :param operator: Operator to find the parameter to change for (str).
        :param print_error: Whether to print an error if parameter is nto found.
        :return: The parameter that can be set in the jobmanager .yaml to set the parallelism of the provided operator.
        """
        corresponding_key = ""
        for operator_name_key in self.operator_to_parallelism_mapping.keys():
            if operator_name_key.lower() in operator.lower():
                print(f"Found key '{operator_name_key}' in operator_name '{operator}' ")
                corresponding_key = operator_name_key

        if corresponding_key in self.operator_to_parallelism_mapping:
            return self.operator_to_parallelism_mapping[corresponding_key]
        else:
            if print_error:
                print(f"Error: did not find {operator} in operator_to_parallelism_mapping "
                      f"{self.operator_to_parallelism_mapping}.")

    def gather_source_operators_of_operator(self, operator, topology: [(str, str)]) -> [str]:
        """
        Given an operator and a topology, find the source operators that produce records for the provided operator. If the operator itself
        is a source, it returns an empty list.
        :param operator: Operator to find all source operators for.
        :param topology: Topology of the current jobmanager deployment.
        :return: A list of source operators that produce records for the provided operator.
        """
        if self.operator_is_a_source(operator):
            return [operator]

        source_operators = set()
        for (l_operator, r_operator) in topology:
            if r_operator == operator:
                l_source_operators = self.gather_source_operators_of_operator(l_operator, topology)
                source_operators.update(l_source_operators)

        return list(source_operators)
