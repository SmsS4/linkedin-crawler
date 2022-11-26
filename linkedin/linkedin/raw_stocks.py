import json


def get_raw_stocks() -> list[tuple[str, str]]:
    with open("stocks.json") as f:
        data = json.load(f)
    return [(row["symbol"], row["name"]) for row in data["data"]["table"]["rows"]]
