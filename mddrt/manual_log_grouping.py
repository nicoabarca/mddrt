from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from time import timedelta


class ManualLogGrouping:
    def __init__(
        self,
        log: pd.DataFrame,
        activities_to_group: set[str],
        case_id_key: str = "case:concept:name",
        activity_id_key: str = "concept:name",
        start_timestamp_key: str | None = "start_timestamp",
        timestamp_key: str = "time:timestamp",
    ) -> None:
        self.log: pd.DataFrame = log
        self.activities_to_group: set[str] = activities_to_group
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
        self.get_grouped_log()

    def validate_activities_to_group(self):
        unique_activities_names = set(self.log[self.activity_id_key].unique())
        diff_between_sets = self.activities_to_group - unique_activities_names
        if len(diff_between_sets) != 0:
            error_message = f"Activities to group: {diff_between_sets} are not in log activity names."
            raise ValueError(error_message)

    def group(self):
        cases_grouped_by_id = self.log.groupby(self.case_id_key, dropna=True, sort=False)
        for _, actual_case in cases_grouped_by_id:
            self.iterate_case_rows(actual_case)

    def iterate_case_rows(self, df: pd.DataFrame):
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

        self.activities_left_to_be_grouped.discard(incoming_activity[self.activity_id_key])

    def add_activity_to_log(self, row: pd.Series) -> None:
        self.grouped_log[str(self.actual_activities_index)] = row
        self.actual_activities_index += 1

    def merge_activities(self, base_activity: pd.Series, incoming_activity: pd.Series) -> pd.Series:
        activity_data = []
        for column_name in self.log_columns:
            if column_name in [self.case_id_key, self.start_timestamp_key, self.timestamp_key]:
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
        if column_name == self.start_timestamp_key:
            return min(base_activity[self.start_timestamp_key], incoming_activity[self.start_timestamp_key])
        return max(base_activity[self.start_timestamp_key], incoming_activity[self.start_timestamp_key])

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
            if "[" in base_value or "]" in base_value:
                return f"{base_value.replace(']', '')},{incoming_value}]"
            return f"[{base_value},{incoming_value}]"
        if pd.api.types.is_datetime64_any_dtype(type(base_value)):
            return min(base_value, incoming_value)
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
    activities_to_group: set[str],
    case_id_key: str = "case:concept:name",
    activity_id_key: str = "concept:name",
    start_timestamp_key: str | None = "start_timestamp",
    timestamp_key: str = "time:timestamp",
) -> pd.DataFrame:
    manual_log_grouping = ManualLogGrouping(
        log, activities_to_group, case_id_key, activity_id_key, start_timestamp_key, timestamp_key
    )
    return manual_log_grouping.get_grouped_log()
