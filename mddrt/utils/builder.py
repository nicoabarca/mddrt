import pandas as pd
import numpy as np
from datetime import timedelta
from sys import maxsize
from mddrt.drt_parameters import DirectlyRootedTreeParameters


def calculate_cases_metrics(
    log: pd.DataFrame,
    params: DirectlyRootedTreeParameters,
    num_mandatory_activities=None,
) -> pd.DataFrame:
    case_ids = sorted(log[params.case_id_key].unique())

    if params.calculate_flexibility and num_mandatory_activities is None:
        mandatory_activities = log.loc[log[params.case_id_key] == case_ids[0]][params.activity_key].unique()
        counter = 0
        for case_id in case_ids:
            log_case = log.loc[log[params.case_id_key] == case_id]
            case_activities = log_case[params.activity_key].unique()

            non_mandatory_activities = []
            for mandatory_activity in mandatory_activities:
                if not np.isin(mandatory_activity, case_activities):
                    non_mandatory_activities.append(mandatory_activity)

            for non_mandatory_activity in non_mandatory_activities:
                mandatory_activities = np.delete(
                    mandatory_activities, np.where(mandatory_activities == non_mandatory_activity)
                )
            counter += 1
            print(f"{counter}/{len(case_ids)}")

        num_mandatory_activities = len(mandatory_activities)

    log_metrics = []

    for case_id in case_ids:
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
    log_metrics = pd.DataFrame(log_metrics)

    print(log_metrics)
    print("sum Rework", sum(log_metrics["Rework"]))
    print("sum Optionality", sum(log_metrics["Optionality"]))

    return log_metrics


def get_start_activities(cases_grouped_by_id: pd.DataFrame, params: DirectlyRootedTreeParameters):
    start_activities = [*dict(cases_grouped_by_id[params.activity_key].first().value_counts()).keys()]
    return start_activities


def get_end_activities(cases_grouped_by_id: pd.DataFrame, params: DirectlyRootedTreeParameters):
    end_activities = [*dict(cases_grouped_by_id[params.activity_key].last().value_counts()).keys()]
    return end_activities


def create_case_data(params: DirectlyRootedTreeParameters, id: int):
    case_data = {}
    case_data["frequency"] = 0
    case_data["id"] = id
    data = {
        "total": 0,
        "total_case": 0,
        "remainder": 0,
        "accumulated": 0,
        "statistic": 0,
        "max": 0,
        "min": maxsize,
    }
    if params.calculate_cost:
        case_data["cost"] = data.copy()

    if params.calculate_quality:
        case_data["quality"] = data.copy()

    if params.calculate_flexibility:
        case_data["flexibility"] = data.copy()

    if params.calculate_time:
        data = {
            "total": pd.Timedelta(days=0),
            "total_case": pd.Timedelta(days=0),
            "remainder": pd.Timedelta(days=0),
            "accumulated": pd.Timedelta(days=0),
            "statistic": pd.Timedelta(days=0),
            "max": pd.Timedelta(days=0),
            "min": timedelta(microseconds=2**63 - 1),
        }
        case_data["time"] = data
    return case_data
