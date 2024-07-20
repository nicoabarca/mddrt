import pandas as pd
from typing import Union


def log_formatter(log: pd.DataFrame, format: dict, timestamp_format: Union[str, None] = None):
    """
    Formats the log DataFrame based on the provided format dictionary.

    Args:
        log (pd.DataFrame): The log DataFrame to be formatted.
        format (dict): The format dictionary containing the column mappings.
        timestamp_format (str | None): The format string for the timestamp column. Defaults to None.

    Returns:
        pd.DataFrame: The formatted log DataFrame.
    """
    log = log.rename(
        columns={
            format["case:concept:name"]: "case:concept:name",
            format["concept:name"]: "concept:name",
            format["time:timestamp"]: "time:timestamp",
        }
    )

    if format["start_timestamp"] == "":
        log["start_timestamp"] = log["time:timestamp"].copy()
    else:
        log = log.rename(columns={format["start_timestamp"]: "start_timestamp"})

    if format["cost:total"] == "":
        log["cost:total"] = 0
    else:
        log = log.rename(columns={format["cost:total"]: "cost:total"})

    if format["org:resource"] == "":
        log["org:resoure"] = ""
    else:
        log = log.rename(columns={format["org:resource"]: "org:resource"})

    log["time:timestamp"] = pd.to_datetime(log["time:timestamp"], utc=True, format=timestamp_format)
    log["start_timestamp"] = pd.to_datetime(log["start_timestamp"], utc=True, format=timestamp_format)

    log["case:concept:name"] = log["case:concept:name"].astype(str)
    return log
