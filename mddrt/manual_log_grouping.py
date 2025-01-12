from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from tqdm import tqdm

if TYPE_CHECKING:
    from time import timedelta


class ManualLogGrouping:
    def __init__(
        self,
        log: pd.DataFrame,
        activities_to_group: set[str],
        group_name: str,
        case_id_key: str = "case:concept:name",
        activity_id_key: str = "concept:name",
        start_timestamp_key: str | None = "start_timestamp",
        timestamp_key: str = "time:timestamp",
    ) -> None:
        self.log: pd.DataFrame = log
        self.activities_to_group: list[str] = activities_to_group
        self.group_name: str = self.set_group_name(group_name, activities_to_group)
        self.case_id_key: str = case_id_key
        self.activity_id_key: str = activity_id_key
        self.start_timestamp_key: str | None = start_timestamp_key
        self.timestamp_key: str = timestamp_key
        self.log_columns: pd.Index[str] = self.log.columns
        self.activities_left_to_be_grouped: set[str] = activities_to_group.copy()
        self.grouped_log: dict = {}
        self.actual_activities_index: int = 0
        self.actual_activities_grouping_index: int = 0
        self.validate_activities_to_group()
        self.group()

    def set_group_name(self, group_name: str | None, activities_to_group: list[str]) -> str:
        return group_name if group_name else "[" + ",<br/>".join(activities_to_group) + "]"

    def validate_activities_to_group(self) -> None | ValueError:
        unique_activities_names = set(self.log[self.activity_id_key].unique())
        diff_between_sets = set(self.activities_to_group) - unique_activities_names
        has_duplicated = len(self.activities_to_group) != len(set(self.activities_to_group))
        if len(diff_between_sets) != 0:
            error_message = f"Activities to group: {diff_between_sets} are not in log activity names or activities to group is empty."
            raise ValueError(error_message)
        if has_duplicated:
            error_message = "Activities to group has duplicated elements. Keep only one occurrence of activity name."
            raise ValueError(error_message)

    def group(self) -> None:
        cases_grouped_by_id = self.log.groupby(self.case_id_key, dropna=True, sort=False)
        print("Manual log grouping:")
        for _, actual_case in tqdm(cases_grouped_by_id):
            self.iterate_case_rows(actual_case)

    def iterate_case_rows(self, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            if self.is_activities_left_to_be_grouped_empty():
                self.reset_activities_left_to_be_grouped()
            if self.is_activity_in_activities_left_to_be_grouped(row):
                self.group_activities(row)
            else:
                self.add_activity_to_log(row)

    def group_activities(self, incoming_activity: pd.Series) -> None:
        if self.is_activities_left_to_be_grouped_full():
            self.actual_activities_grouping_index = self.actual_activities_index
            self.add_activity_to_log(incoming_activity)
        else:
            base_activity = self.grouped_log[str(self.actual_activities_grouping_index)]
            self.merge_activities(base_activity, incoming_activity)

        self.activities_left_to_be_grouped.remove(incoming_activity[self.activity_id_key])

    def add_activity_to_log(self, row: pd.Series) -> None:
        self.grouped_log[str(self.actual_activities_index)] = row
        self.actual_activities_index += 1

    def merge_activities(self, base_activity: pd.Series, incoming_activity: pd.Series) -> pd.Series:
        activity_data = []
        for column_name in self.log_columns:
            if column_name in [self.case_id_key, self.activity_id_key, self.start_timestamp_key, self.timestamp_key]:
                value = self.merge_value_based_on_column_name(column_name, base_activity, incoming_activity)
            else:
                value = self.merge_value_based_on_data_type(column_name, base_activity, incoming_activity)
            activity_data.append(value)
        merged_activities_data = pd.Series(activity_data, index=base_activity.index.tolist())
        self.grouped_log[str(self.actual_activities_grouping_index)] = merged_activities_data

    def is_activities_left_to_be_grouped_full(self) -> bool:
        return len(self.activities_left_to_be_grouped) == len(self.activities_to_group)

    def is_activities_left_to_be_grouped_empty(self) -> bool:
        return len(self.activities_left_to_be_grouped) == 0

    def is_activity_in_activities_left_to_be_grouped(self, row: pd.Series) -> bool:
        return row[self.activity_id_key] in self.activities_left_to_be_grouped

    def is_activity_in_activities_to_group(self, row: pd.Series) -> bool:
        return row[self.activity_id_key] in self.activities_to_group

    def reset_activities_left_to_be_grouped(self) -> None:
        self.activities_left_to_be_grouped = self.activities_to_group.copy()

    def merge_value_based_on_column_name(
        self, column_name: str, base_activity: pd.Series, incoming_activity: pd.Series
    ) -> int | timedelta:
        if column_name == self.case_id_key:
            return base_activity[self.case_id_key]
        if column_name == self.activity_id_key:
            return self.group_name
        if column_name == self.start_timestamp_key:
            return min(base_activity[self.start_timestamp_key], incoming_activity[self.start_timestamp_key])
        return max(base_activity[self.timestamp_key], incoming_activity[self.timestamp_key])

    def merge_value_based_on_data_type(
        self, column_name: str, base_activity: pd.Series, incoming_activity: pd.Series
    ) -> float | int | str | timedelta:
        base_value = base_activity[column_name]
        incoming_value = incoming_activity[column_name]
        if (
            pd.api.types.is_integer(base_value)
            or pd.api.types.is_float(base_value)
            or pd.api.types.is_complex(base_value)
        ):
            return base_value + incoming_value
        if pd.api.types.is_string_dtype(type(base_value)):
            if "[" in base_value or "]" in base_value:  # TODO: ordenarlos de forma alfabetica
                return f"{base_value.replace(']', '')},{incoming_value}]"
            return f"[{base_value},{incoming_value}]"
        if pd.api.types.is_datetime64_any_dtype(type(base_value)):
            return max(base_value, incoming_value)
        if pd.api.types.is_timedelta64_dtype(type(base_value)):
            return base_value + incoming_value
        if pd.api.types.is_categorical_dtype(type(base_value)):
            return f"{base_value}-{incoming_value}"
        error_message = f"Unsupported data type: {type(base_value).__name__}. Try convert it before manual grouping"
        raise TypeError(error_message)

    def get_grouped_log(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.grouped_log, orient="index")


def manual_log_grouping(
    log: pd.DataFrame,
    activities_to_group: list[str],
    group_name: str | None = None,
    case_id_key: str = "case:concept:name",
    activity_id_key: str = "concept:name",
    start_timestamp_key: str | None = "start_timestamp",
    timestamp_key: str = "time:timestamp",
) -> pd.DataFrame:
    """
    Groups specified activities in a process log into a single activity group.

    This function takes a process log as a pandas DataFrame and groups the specified
    activities defined in `activities_to_group`. It uses the provided case identifier,
    activity identifier, and timestamp keys to perform the grouping. Optionally, a
    `start_timestamp_key` can be provided for logs with start times.

    Args:
        log (pd.DataFrame): The input process log DataFrame containing the events.
        activities_to_group (list[str]): A list of activity names (strings) to group together.
        group_name (str | None): Name of the node with the grouped activities. Defaults to None.
        case_id_key (str, optional): The key in the DataFrame that represents the case ID.
            Defaults to "case:concept:name".
        activity_id_key (str, optional): The key in the DataFrame that represents the activity name.
            Defaults to "concept:name".
        start_timestamp_key (str | None, optional): The key in the DataFrame representing the start
            timestamp of the events. Can be None if not available. Defaults to "start_timestamp".
        timestamp_key (str, optional): The key in the DataFrame representing the event timestamp.
            Defaults to "time:timestamp".

    Returns:
        pd.DataFrame: A new DataFrame with the grouped activities, keeping the original structure
        of the log but modifying the activities defined in `activities_to_group`.
    """
    manual_log_grouping = ManualLogGrouping(
        log, activities_to_group, group_name, case_id_key, activity_id_key, start_timestamp_key, timestamp_key
    )
    return manual_log_grouping.get_grouped_log()
