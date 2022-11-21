OPERATOR_TO_TOPIC_MAPPING = {
    "bidssource": "bids_topic",
    "auctionssource": "auction_topic",
    "personsource": "person_topic"
}


def __subtractSourceNameFromOperatorName(operatorName: str):
    for sourceName in OPERATOR_TO_TOPIC_MAPPING.keys():
        if sourceName in operatorName.lower():
            return sourceName
    print(f"Error: could not determine sourceName from operatorName '{operatorName}'")


def getTopicFromOperatorName(operatorName):
    sourceName = __subtractSourceNameFromOperatorName(operatorName)
    if sourceName in OPERATOR_TO_TOPIC_MAPPING:
        return OPERATOR_TO_TOPIC_MAPPING[sourceName]
    else:
        print(f"Error: could not fetch topic from operatorName '{operatorName}'")