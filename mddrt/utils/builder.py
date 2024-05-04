import pandas as pd
import numpy as np
from mddrt.drt_parameters import DirectlyRootedTreeParameters


def calculate_cases_metrics(
    log: pd.DataFrame,
    case_id_key: str,
    activity_key: str,
    timestamp_key: str,
    start_timestamp_key: str,
    cost_key: str,
    calculate_duration: bool = True,
    calculate_cost: bool = True,
    calculate_repeatability=True,  # measure of quality
    calculate_optionality=True,  # measure of flexibility
    num_mandatory_activities=None,
) -> pd.DataFrame:
    case_ids = sorted(log[case_id_key].unique())

    if calculate_optionality and num_mandatory_activities is None:
        mandatory_activities = log.loc[log[case_id_key] == case_ids[0]][activity_key].unique()

        for case_id in case_ids:
            log_case = log.loc[log[case_id_key] == case_id]
            case_activities = log_case[activity_key].unique()

            non_mandatory_activities = []
            for mandatory_activity in mandatory_activities:
                if not np.isin(mandatory_activity, case_activities):
                    non_mandatory_activities.append(mandatory_activity)

            for non_mandatory_activity in non_mandatory_activities:
                mandatory_activities = np.delete(
                    mandatory_activities, np.where(mandatory_activities == non_mandatory_activity)
                )

        num_mandatory_activities = len(mandatory_activities)

    log_metrics = []

    for case_id in case_ids:
        log_case = log.loc[log[case_id_key] == case_id]

        case_metrics = {}

        case_metrics["Case Id"] = case_id

        if calculate_duration:
            case_start = log_case[start_timestamp_key].min()
            case_complete = log_case[timestamp_key].max()

            case_metrics["Duration"] = (case_complete - case_start).total_seconds()

        if calculate_cost:
            case_metrics["Cost"] = log_case[cost_key].sum()

        if calculate_repeatability or calculate_optionality:
            unique_activities = log_case[activity_key].unique()
            num_unique_activities = len(unique_activities)

            if calculate_repeatability:
                case_metrics["Repeatability"] = 1 - num_unique_activities / len(log_case)

            if calculate_optionality:
                case_metrics["Optionality"] = (
                    num_unique_activities - num_mandatory_activities
                ) / num_unique_activities

            case_metrics["Optional Activities"] = num_unique_activities - num_mandatory_activities
            case_metrics["Unique Activities"] = num_unique_activities
            case_metrics["Total Activities"] = len(log_case)

        log_metrics.append(case_metrics)

    return pd.DataFrame(log_metrics)
