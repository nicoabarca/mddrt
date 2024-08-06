import pandas as pd
from typing import Tuple
from datetime import timedelta
from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.utils.builder import calculate_cases_metrics, dimensions_to_calculate
from mddrt.node.node import Node


class DirectlyRootedTreeBuilder:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log: pd.DataFrame = log
        self.params: DirectlyRootedTreeParameters = params
        self.tree: Node = None
        self.cases: dict = None
        self.dimensions_to_calculate: dict = dimensions_to_calculate(params)
        self.build()

    def build(self) -> None:
        cases_grouped_by_id = self.log.groupby(self.params.case_id_key, dropna=True, sort=False)
        self.build_cases(cases_grouped_by_id)
        self.build_tree()
        self.update_root()

    def build_cases(self, cases_grouped_by_id: pd.Grouper) -> None:
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

    def build_case_activities(self, case: Tuple[int, pd.DataFrame]) -> list:
        case_activities = []
        for _, activity in case[1].iterrows():
            activity_dict = {}
            activity_dict["name"] = activity[self.params.activity_key]
            if self.params.calculate_cost:
                activity_dict["cost"] = activity[self.params.cost_key]
            if self.params.calculate_time:
                activity_dict["time"] = activity[self.params.timestamp_key] - activity[self.params.start_timestamp_key]
            case_activities.append(activity_dict)
        return case_activities

    def build_tree(self) -> None:
        root = Node(name="root", depth=-1)
        for _, current_case in self.cases.items():
            parent_node = root
            current_node = None
            for depth, activity in enumerate(current_case["activities"]):
                current_node = parent_node.get_child_by_name_and_depth(activity["name"], depth)
                if not current_node:
                    current_node = Node(activity["name"], depth)
                    current_node.set_parent(parent_node)
                    parent_node.add_children(current_node)

                current_node.update_frequency()

                for dimension in self.dimensions_to_calculate:
                    current_node.update_dimensions_data(dimension, depth, current_case)
                parent_node = current_node

                # debug only code
                print(parent_node)
            breakpoint()

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

    def get_tree(self) -> Node:
        return self.tree
