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
    # Also add prometheus operator names to operator_to_parallelism_mapping

    def __init__(self):
        new_operator_to_parallelism_mapping = dict(self.operator_to_parallelism_mapping)
        for operator_name, parameter in self.operator_to_parallelism_mapping.items():
            stripped_operator_name = self.convertOperatorNameToPrometheusOperatorName(operator_name)
            new_operator_to_parallelism_mapping[stripped_operator_name] = parameter
        self.operator_to_parallelism_mapping = new_operator_to_parallelism_mapping

    @staticmethod
    def convertOperatorNameToPrometheusOperatorName(operatorName: str):
        """
        The operator names of Prometheus differ from the Jobmanager. While the jobmanager supports " ", ".", and "-",
        Prometheus presents the characters as a "_". To ensure compatibility between the prometheus metrics and the
        jobmanager metrics, characters in the operator names are replaced with "_".
        :param operatorName: Operatorname to replace characters with.
        :return: Operator name that has all forbidden characters replaced with a "_"
        """
        unsupportedCharacters = ["-&gt", " ", ",", ".", "-", ";", "/", ">"]
        for unsupportedCharacter in unsupportedCharacters:
            operatorName = operatorName.replace(unsupportedCharacter, "_")
        return operatorName


    def __subtractSourceNameFromOperatorName(self, operatorName: str, printError=True):
        """
        For all sourceNames in self.operator_to_topic_naming, check whether the sourceName is contained in operatorName
        and return the sourceName
        """
        for sourceName in self.operator_to_topic_naming.keys():
            if sourceName in operatorName.lower():
                return sourceName
        if printError:
            print(f"Error: could not determine sourceName from operatorName '{operatorName}'")

    def operatorIsASource(self, operatorName: str):
        """
        Determine whether operatorName is a source.
        """
        return self.__subtractSourceNameFromOperatorName(operatorName, printError=False) is not None

    def getTopicFromOperatorName(self, operatorName, printError=True):
        sourceName = self.__subtractSourceNameFromOperatorName(operatorName, printError=False)
        if sourceName in self.operator_to_topic_naming:
            return self.operator_to_topic_naming[sourceName]
        else:
            if printError:
                print(f"Error: could not fetch topic from operatorName '{operatorName}'")

    def getParallelismParameterOfOperator(self, operator, printError: bool = True):
        correspondingKey = ""
        for operatorNameKey in self.operator_to_parallelism_mapping.keys():
            if operatorNameKey.lower() in operator.lower():
                print(f"Found key '{operatorNameKey}' in operatorName '{operator}' ")
                correspondingKey = operatorNameKey

        if correspondingKey in self.operator_to_parallelism_mapping:
            return self.operator_to_parallelism_mapping[correspondingKey]
        else:
            if printError:
                print(f"Error: did not find {operator} in operator_to_parallelism_mapping "
                      f"{self.operator_to_parallelism_mapping}.")
