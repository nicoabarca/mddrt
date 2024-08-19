from __future__ import annotations

from itertools import accumulate
from sys import maxsize
from typing import TYPE_CHECKING, Literal

import pandas as pd
from tqdm import tqdm

if TYPE_CHECKING:
    from mddrt.drt_parameters import DirectlyRootedTreeParameters


def calculate_cases_metrics(
    log: pd.DataFrame,
    params: DirectlyRootedTreeParameters,
    num_mandatory_activities: int | None = None,
) -> pd.DataFrame:
    case_ids = sorted(log[params.case_id_key].unique())

    if params.calculate_flexibility and num_mandatory_activities is None:
        mandatory_activities = log.loc[log[params.case_id_key] == case_ids[0]][params.activity_key].unique()
        mandatory_activities_set = set(mandatory_activities)
        print("Calculating log mandatory activities: ")
        for case_id in tqdm(case_ids):
            log_case = log.loc[log[params.case_id_key] == case_id]
            case_activities = log_case[params.activity_key].unique()
            mandatory_activities_set = mandatory_activities_set.intersection(case_activities)
        num_mandatory_activities = len(mandatory_activities_set)

    log_metrics = []
    print("Calculating log metrics: ")
    for case_id in tqdm(case_ids):
        log_case = log.loc[log[params.case_id_key] == case_id]
        case_metrics = {}
        case_metrics["Case Id"] = case_id

        if params.calculate_time:
            case_start = log_case[params.start_timestamp_key].min()
            case_complete = log_case[params.timestamp_key].max()
            case_metrics["Duration"] = case_complete - case_start

        if params.calculate_cost:
            case_metrics["Cost"] = log_case[params.cost_key].sum()

        if params.calculate_quality or params.calculate_flexibility:
            unique_activities = log_case[params.activity_key].unique()
            num_unique_activities = len(unique_activities)

            if params.calculate_quality:
                case_metrics["Rework"] = len(log_case) - num_unique_activities

            if params.calculate_flexibility:
                case_metrics["Optionality"] = num_unique_activities - num_mandatory_activities

            case_metrics["Optional Activities"] = num_unique_activities - num_mandatory_activities
            case_metrics["Unique Activities"] = num_unique_activities
            case_metrics["Total Activities"] = len(log_case)

        log_metrics.append(case_metrics)
    return pd.DataFrame(log_metrics)


def create_dimensions_data() -> dict:
    return {
        "cost": create_default_data("numeric"),
        "quality": create_default_data("numeric"),
        "flexibility": create_default_data("numeric"),
        "time": create_default_data("timedelta"),
    }


def create_default_data(data_type: Literal["numeric", "timedelta"]) -> dict:
    if data_type == "numeric":
        return {
            "total": 0,
            "total_case": 0,
            "remainder": 0,
            "accumulated": 0,
            "max": 0,
            "min": maxsize,
        }
    return {
        "lead": pd.Timedelta(days=0),
        "lead_case": pd.Timedelta(days=0),
        "lead_remainder": pd.Timedelta(days=0),
        "lead_accumulated": pd.Timedelta(days=0),
        "max": pd.Timedelta(days=0),
        "min": pd.Timedelta.max,
        "service": pd.Timedelta(days=0),
        "waiting": pd.Timedelta(days=0),
    }


def activities_dimension_cumsum(
    current_case: dict,
    dimension: Literal["cost", "time", "flexibility", "quality"],
) -> list[int | pd.Timedelta]:
    activities = current_case["activities"]
    if dimension == "time":
        dimension_data = [item["service_time"] + item["waiting_time"] for item in activities]
    elif dimension == "cost":
        dimension_data = [item[dimension] for item in activities]
    else:
        dimension_data = [current_case[dimension] / len(current_case["activities"])] * len(current_case["activities"])

    return list(accumulate(dimension_data))


def dimensions_to_calculate(params: DirectlyRootedTreeParameters) -> list[str]:
    dimensions_to_calculate = []
    if params.calculate_cost:
        dimensions_to_calculate.append("cost")
    if params.calculate_time:
        dimensions_to_calculate.append("time")
    if params.calculate_flexibility:
        dimensions_to_calculate.append("flexibility")
    if params.calculate_quality:
        dimensions_to_calculate.append("quality")

    return dimensions_to_calculate
