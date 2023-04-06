class Queries:
    """
    Helperclass containing all possible autoscalers used by the experiments.
    """
    QUERY_1 = "1"
    QUERY_2 = "2"
    QUERY_3 = "3"
    QUERY_5 = "5"
    QUERY_8 = "8"
    QUERY_11 = "11"

    @staticmethod
    def get_all_queries() -> [str]:
        return [
            Queries.QUERY_1,
            Queries.QUERY_2,
            Queries.QUERY_3,
            Queries.QUERY_5,
            Queries.QUERY_8,
            Queries.QUERY_11,
        ]

    @staticmethod
    def is_query(query) -> bool:
        return Queries.get_all_queries().__contains__(query)
