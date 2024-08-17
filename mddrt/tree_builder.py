from datetime import timedelta
from typing import Hashable, List, Tuple

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.tree_node import TreeNode
from mddrt.utils.builder import calculate_cases_metrics, dimensions_to_calculate


class DirectlyRootedTreeBuilder:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log: pd.DataFrame = log
        self.params: DirectlyRootedTreeParameters = params
        self.tree: TreeNode = TreeNode(name="root", depth=-1)
        self.cases: dict = {}
        self.dimensions_to_calculate: List[str] = dimensions_to_calculate(params)
        self.build()

    def build(self) -> None:
        cases_grouped_by_id = self.log.groupby(self.params.case_id_key, dropna=True, sort=False)
        self.build_cases(cases_grouped_by_id)
        self.build_tree()
        # TODO: fix update root methos based on new time information
        # self.update_root()

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

    def build_case_activities(self, case: Tuple[Hashable, pd.DataFrame]) -> list:
        case_activities = []
        case_df = case[1]
        for i in range(len(case_df)):
            actual_activity = case_df.iloc[i]
            activity_dict = {}
            activity_dict["name"] = actual_activity[self.params.activity_key]
            if self.params.calculate_cost:
                activity_dict["cost"] = actual_activity[self.params.cost_key]
            if self.params.calculate_time:
                service_time = (
                    actual_activity[self.params.timestamp_key] - actual_activity[self.params.start_timestamp_key]
                )
                activity_dict["service_time"] = service_time

                prev_activity = case_df.iloc[i] if i == 0 else case_df.iloc[i - 1]
                waiting_time = (
                    actual_activity[self.params.start_timestamp_key] - prev_activity[self.params.timestamp_key]
                    if i > 0
                    else pd.Timedelta(0)
                )
                activity_dict["waiting_time"] = waiting_time
            case_activities.append(activity_dict)
        return case_activities

    def build_tree(self) -> None:
        root = self.tree
        for current_case in self.cases.values():
            parent_node = root
            current_node = None
            for depth, activity in enumerate(current_case["activities"]):
                current_node = parent_node.get_child_by_name_and_depth(activity["name"], depth)
                if not current_node:
                    current_node = TreeNode(activity["name"], depth)
                    current_node.set_parent(parent_node)
                    parent_node.add_children(current_node)

                current_node.update_frequency()
                for dimension in self.dimensions_to_calculate:
                    current_node.update_dimension(dimension, depth, current_case)
                parent_node = current_node
        self.tree = root

    def update_root(self) -> None:
        self.tree.frequency = sum(node.frequency for node in self.tree.children)
        for dimension in self.dimensions_to_calculate:
            default = 0 if dimension != "time" else timedelta()
            self.tree.dimensions_data[dimension]["total"] = sum(
                [node.dimensions_data[dimension]["total"] for node in self.tree.children], default
            )
            self.tree.dimensions_data[dimension]["total_case"] = sum(
                [node.dimensions_data[dimension]["total_case"] for node in self.tree.children], default
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
            raise ValueError("Tree not built yet.")
        return self.tree
