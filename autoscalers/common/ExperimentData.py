class ExperimentData:
    operator_to_topic_naming = {
        "bidssource": "bids_topic",
        "auctionssource": "auction_topic",
        "personsource": "person_topic"
    }

    def __subtractSourceNameFromOperatorName(self, operatorName: str, printError=True):

        for sourceName in self.operator_to_topic_naming.keys():
            if sourceName in operatorName.lower():
                return sourceName
        if printError:
            print(f"Error: could not determine sourceName from operatorName '{operatorName}'")

    def getTopicFromOperatorName(self, operatorName, printError=True):
        sourceName = self.__subtractSourceNameFromOperatorName(operatorName, printError=False)
        if sourceName in self.operator_to_topic_naming:
            return self.operator_to_topic_naming[sourceName]
        else:
            if printError:
                print(f"Error: could not fetch topic from operatorName '{operatorName}'")

    operator_to_parallelism_mapping = {
        # Sources
        "BidsSource": "--p-bids-source",
        "AuctionsSource": "--p-auction-source",
        "PersonSource": "--p-person-source",

        # Query 1
        "Mapper": "--p-map",
        # Query 2
        "FlatMapFilter": "--p-flatMap",
        # Query 3
        "IncrementalJoin": "--p-join",
        # Query 5
        "SlidingWindow": "--p-window",
        # Query 8
        # Todo: undefined
        # Query 11
        "SessionWindow": "--p-window",

        # Sinks
        "LatencySink": "--p-sink",
    }

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
