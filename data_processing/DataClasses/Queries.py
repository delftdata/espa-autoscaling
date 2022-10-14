class Queries:
    """
    Helperclass containing all possible autoscalers used by the experiments.
    """
    QUERY_1 = "1"
    QUERY_3 = "3"
    QUERY_11 = "11"

    @staticmethod
    def getAllQueries() -> [str]:
        return [
            Queries.QUERY_1,
            Queries.QUERY_3,
            Queries.QUERY_11
        ]

    @staticmethod
    def isQuery(query) -> bool:
        return Queries.getAllQueries().__contains__(query)
