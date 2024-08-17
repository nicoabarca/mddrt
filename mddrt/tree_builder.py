from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pandas as pd

from mddrt.tree_node import TreeNode
from mddrt.utils.builder import calculate_cases_metrics, dimensions_to_calculate

if TYPE_CHECKING:
    from collections.abc import Hashable

    from pandas.core.groupby import DataFrameGroupBy

    from mddrt.drt_parameters import DirectlyRootedTreeParameters


class DirectlyRootedTreeBuilder:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log: pd.DataFrame = log
        self.params: DirectlyRootedTreeParameters = params
        self.tree: TreeNode = TreeNode(name="root", depth=-1)
        self.cases: dict = {}
        self.dimensions_to_calculate: list[str] = dimensions_to_calculate(params)
        self.build()

    def build(self) -> None:
        cases_grouped_by_id = self.log.groupby(self.params.case_id_key, dropna=True, sort=False)
        self.build_cases(cases_grouped_by_id)
        self.build_tree()
        self.update_root()

    def build_cases(self, cases_grouped_by_id: DataFrameGroupBy) -> None:
        cases = {}
        cases_metrics = calculate_cases_metrics(self.log, self.params)
        for case in cases_grouped_by_id:
            case_id = case[0]
            cases[case_id] = {}
            case_activities = self.build_case_activities(case)
            case_metrics = cases_metrics.loc[cases_metrics["Case Id"] == case_id].iloc[0]
            cases[case_id]["activities"] = case_activities
            metrics_mapping = {"cost": "Cost", "time": "Duration", "flexibility": "Optionality", "quality": "Rework"}
            for dimension in self.dimensions_to_calculate:
                cases[case_id][dimension] = case_metrics[metrics_mapping[dimension]]
        self.cases = cases

    def build_case_activities(self, case: tuple[Hashable, pd.DataFrame]) -> list[dict[str, any]]:
        case_df = case[1]
        return [self.build_activity_dict(case_df, i) for i in range(len(case_df))]

    def build_activity_dict(self, case_df: pd.DataFrame, index: int) -> dict[str, any]:
        actual_activity = case_df.iloc[index]
        activity_dict = {
            "name": actual_activity[self.params.activity_key],
        }
        if self.params.calculate_cost:
            activity_dict["cost"] = actual_activity[self.params.cost_key]
        if self.params.calculate_time:
            activity_dict.update(self.calculate_time_data(case_df, index))
        return activity_dict

    def calculate_time_data(self, case_df: pd.DataFrame, index: int) -> dict[str, pd.Timedelta]:
        actual_activity = case_df.iloc[index]
        service_time = actual_activity[self.params.timestamp_key] - actual_activity[self.params.start_timestamp_key]

        prev_activity = case_df.iloc[index - 1] if index > 0 else None
        waiting_time = (
            actual_activity[self.params.start_timestamp_key] - prev_activity[self.params.timestamp_key]
            if prev_activity is not None
            else pd.Timedelta(0)
        )
        return {"service_time": service_time, "waiting_time": waiting_time}

    def build_tree(self) -> None:
        root = self.tree
        for current_case in self.cases.values():
            self.add_case_to_tree(root, current_case)
        self.tree = root

    def add_case_to_tree(self, root: TreeNode, current_case: dict) -> None:
        parent_node = root
        for depth, activity in enumerate(current_case["activities"]):
            current_node = self.get_or_create_node(parent_node, activity["name"], depth)
            current_node.update_frequency()
            self.update_node_dimensions(current_node, depth, current_case)
            parent_node = current_node

    def get_or_create_node(self, parent_node: TreeNode, activity_name: str, depth: int) -> TreeNode:
        current_node = parent_node.get_child_by_name_and_depth(activity_name, depth)
        if not current_node:
            current_node = TreeNode(activity_name, depth)
            current_node.set_parent(parent_node)
            parent_node.add_children(current_node)
        return current_node

    def update_node_dimensions(self, node: TreeNode, depth: int, current_case: dict) -> None:
        for dimension in self.dimensions_to_calculate:
            node.update_dimension(dimension, depth, current_case)

    def update_root(self) -> None:
        self.update_root_frequency()
        for dimension in self.dimensions_to_calculate:
            if dimension == "time":
                self.update_root_time_dimension()
            else:
                self.update_root_cost_flexibility_quality_dimension(dimension)

    def update_root_frequency(self) -> None:
        self.tree.frequency = sum(node.frequency for node in self.tree.children)

    def update_root_time_dimension(self) -> None:
        self.tree.dimensions_data["time"]["lead"] = sum(
            [node.dimensions_data["time"]["lead"] for node in self.tree.children],
            timedelta(),
        )
        self.tree.dimensions_data["time"]["lead_case"] = sum(
            [node.dimensions_data["time"]["lead_case"] for node in self.tree.children],
            timedelta(),
        )
        self.tree.dimensions_data["time"]["max"] = max(
            node.dimensions_data["time"]["max"] for node in self.tree.children
        )
        self.tree.dimensions_data["time"]["min"] = min(
            node.dimensions_data["time"]["min"] for node in self.tree.children
        )
        self.tree.dimensions_data["time"]["lead_remainder"] = self.tree.dimensions_data["time"]["lead_case"]

    def update_root_cost_flexibility_quality_dimension(self, dimension: str) -> None:
        self.tree.dimensions_data[dimension]["total"] = sum(
            node.dimensions_data[dimension]["total"] for node in self.tree.children
        )
        self.tree.dimensions_data[dimension]["total_case"] = sum(
            node.dimensions_data[dimension]["total_case"] for node in self.tree.children
        )
        self.tree.dimensions_data[dimension]["max"] = max(
            node.dimensions_data[dimension]["max"] for node in self.tree.children
        )
        self.tree.dimensions_data[dimension]["min"] = min(
            node.dimensions_data[dimension]["min"] for node in self.tree.children
        )
        self.tree.dimensions_data[dimension]["remainder"] = self.tree.dimensions_data[dimension]["total_case"]

    def get_tree(self) -> TreeNode:
        if not self.tree:
            msg = "Tree not built yet."
            raise ValueError(msg)
        return self.tree
