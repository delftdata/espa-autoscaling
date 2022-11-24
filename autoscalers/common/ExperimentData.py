class ExperimentData:
    operator_to_topic_naming = {
        "bidssource": "bids_topic",
        "auctionssource": "auction_topic",
        "personsource": "person_topic"
    }

    def __subtractSourceNameFromOperatorName(self, operatorName: str):

        for sourceName in self.operator_to_topic_naming.keys():
            if sourceName in operatorName.lower():
                return sourceName
        print(f"Error: could not determine sourceName from operatorName '{operatorName}'")

    def getTopicFromOperatorName(self, operatorName):
        sourceName = self.__subtractSourceNameFromOperatorName(operatorName)
        if sourceName in self.operator_to_topic_naming:
            return self.operator_to_topic_naming[sourceName]
        else:
            print(f"Error: could not fetch topic from operatorName '{operatorName}'")

    operator_to_parallelism_mapping = {
        # TODO: make all kafka source queries consistent with the parameters. Query 1, 3, and 11 are supported.

        # Query 1
        "Source:_BidsSource": "--p-source",
        "Mapper": "--p-map",
        "LatencySink": "--p-sink",

        # Query 2
        # bid-source: "--p-source"
        # flatmap: "--p-flatMap"

        # Query 3
        "Source:_auctionsSource": "--p-auction-source",
        "Source:_personSource": "--p-person-source",
        "Incrementaljoin": "--p-join",

        # Query 5
        # bid-source: "p-bid-source"
        # Sliding Window: "--p-window"
        # latency-sink: "--p-window"

        # Query 8
        # person source: "p-person-source"
        # aucation source"p-auction-source"
        # latency sink: "p-window"

        # Query 11
        # "Source:_BidsSource": "--p-source",
        "SessionWindow____DummyLatencySink": "--p-window",
    }

    def getParallelismParameterOfOperator(self, operator, printError: bool = True):
        if operator in self.operator_to_parallelism_mapping:
            return self.operator_to_parallelism_mapping[operator]
        else:
            if printError:
                print(f"Error: did not find {operator} in operator_to_parallelism_mapping "
                      f"{self.operator_to_parallelism_mapping}.")
