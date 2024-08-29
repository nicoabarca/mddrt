from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from mddrt.utils.misc import pretty_format_dict

if TYPE_CHECKING:
    import pandas as pd


def log_manual_grouper(
    log: pd.DataFrame,
    activities_to_group: set[str],
    case_id_key: str,
    activity_id_key: str,
    start_timestamp_key: str | None,
    timestamp_key: str,
) -> pd.DataFrame:
    data = defaultdict(list)
    index_to_group = None
    cases_grouped_by_id = log.groupby(case_id_key, dropna=True, sort=False)

    for case in cases_grouped_by_id:
        case_df = case[1]
        for row_index, row in case_df.iterrows():
            if can_group_activities(row[activity_id_key], activities_to_group, data[str(row_index)]):
                if is_index_group_none(index_to_group) or grouped_row_already_is_full(
                    activities_to_group, data[str(index_to_group)]
                ):
                    index_to_group = row_index
                data[str(index_to_group)].append(row)
            else:
                data[str(row_index)] = row

            print(pretty_format_dict(data))
            breakpoint()


def can_group_activities(activity_name: str, activities_to_group: set[str], already_grouped_activities: list[list]):
    first_condition = activity_in_activities_to_group(activity_name, activities_to_group)
    second_condition = activity_not_already_in_activities_to_group(activity_name, already_grouped_activities)
    return first_condition and second_condition


def activity_in_activities_to_group(activity_name: str, activities_to_group: set[str]) -> bool:
    return activity_name in activities_to_group


def activity_not_already_in_activities_to_group(activity_name: str, grouped_activities: list[str]) -> bool:
    return activity_name not in grouped_activities


def merge_activities(base_activity: pd.Series, incoming_activity: pd.Series):
    pass


def grouped_row_already_is_full(activities_to_group: set, grouped_row: list) -> bool:
    return len(activities_to_group) == len(grouped_row)


def is_index_group_none(index_group: int | None) -> bool:
    return index_group is None
