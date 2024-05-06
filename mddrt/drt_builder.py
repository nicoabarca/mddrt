import pandas as pd
from typing import Tuple
from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.utils.builder import (
    calculate_cases_metrics,
    get_start_activities,
    get_end_activities,
    create_case_data,
)
import pprint


class DirectlyRootedTreeBuilder:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log = log
        self.params = params
        self.tree = None
        self.cases = None
        self.start_activities = None
        self.end_activities = None
        self.build()

    def build(self) -> None:
        cases_grouped_by_id = self.log.groupby(self.params.case_id_key, dropna=True, sort=False)
        self.start_activities = get_start_activities(cases_grouped_by_id, self.params)
        self.end_activities = get_end_activities(cases_grouped_by_id, self.params)
        self.cases = self.build_cases(cases_grouped_by_id)
        self.tree = self.build_tree()

    def build_cases(self, cases_grouped_by_id: pd.Grouper) -> dict:
        cases = {}
        cases_metrics = calculate_cases_metrics(self.log, self.params)
        for case in cases_grouped_by_id:
            case_id = case[0]
            cases[case_id] = {}
            case_activities = self.build_case_activities(case)
            case_metrics = cases_metrics.loc[cases_metrics["Case Id"] == case_id].iloc[0]
            cases[case_id]["activities"] = case_activities
            if self.params.calculate_cost:
                cases[case_id]["cost"] = case_metrics["Cost"]
            if self.params.calculate_time:
                cases[case_id]["time"] = case_metrics["Duration"]
            if self.params.calculate_flexibility:
                cases[case_id]["flexibility"] = case_metrics["Optionality"]
            if self.params.calculate_quality:
                cases[case_id]["quality"] = case_metrics["Repeatability"]
        return cases

    def build_case_activities(self, case: Tuple[int, pd.DataFrame]) -> list:
        case_activities = []
        for _, activity in case[1].iterrows():
            activity_dict = {}
            activity_dict["name"] = activity[self.params.activity_key]
            if self.params.calculate_cost:
                activity_dict["cost"] = activity[self.params.cost_key]
            if self.params.calculate_time:
                activity_dict["time"] = (
                    activity[self.params.timestamp_key] - activity[self.params.start_timestamp_key]
                ).total_seconds()
            case_activities.append(activity_dict)
        return case_activities

    def build_tree(self):
        tree = {}
        for case_id, case in self.cases.items():
            case_data = create_case_data(self.params)
            if self.params.calculate_cost:
                case_data["cost"]["total_case"] = case["cost"]
            if self.params.calculate_time:
                case_data["time"]["total_case"] = case["time"]
            tree = self.nest_activities(tree, case, 0, case_data)
            # TODO: check for total_cost, max_cost, min_cost, total_time, max_time, min_time of all cases

            # min_state_cost, max_state_cost = float(int), 0
            # min_state_time, max_state_time = float(int), 0
        print(tree)
        return tree

    def nest_activities(self, tree: dict, current_case: dict, depth: int, case_data: dict):
        current_activity_name = current_case["activities"][depth]["name"]
        if tree.get(current_activity_name) is None:
            tree[current_activity_name] = {"data": case_data, "childrens": {}}
        tree[current_activity_name]["data"]["frequency"] += 1

        # TODO: make this conditionals cleaner
        if self.params.calculate_cost:
            # ERROR: here in acc cost and rem cost
            activity_cost = current_case["activities"][depth]["cost"]
            accumulated_cost = (
                tree[current_activity_name]["data"]["cost"]["accumulated"] + activity_cost
            )
            remainder_cost = (
                tree[current_activity_name]["data"]["cost"]["remainder"] - activity_cost
            )
            tree[current_activity_name]["data"]["cost"]["total"] += activity_cost
            tree[current_activity_name]["data"]["cost"]["total_case"] += current_case["cost"]
            tree[current_activity_name]["data"]["cost"]["accumulated"] += accumulated_cost
            tree[current_activity_name]["data"]["cost"]["remainder"] += remainder_cost
            tree[current_activity_name]["data"]["cost"]["max"] = max(
                tree[current_activity_name]["data"]["cost"]["max"], activity_cost
            )
            tree[current_activity_name]["data"]["cost"]["min"] = min(
                tree[current_activity_name]["data"]["cost"]["min"], activity_cost
            )

        if self.params.calculate_time:
            # ERROR: here in acc time and rem time
            activity_time = current_case["activities"][depth]["time"]
            accumulated_time = (
                tree[current_activity_name]["data"]["time"]["accumulated"] + activity_time
            )
            remainder_time = (
                tree[current_activity_name]["data"]["time"]["remainder"] - activity_time
            )
            tree[current_activity_name]["data"]["time"]["total"] += activity_time
            tree[current_activity_name]["data"]["time"]["total_case"] += current_case["time"]
            tree[current_activity_name]["data"]["time"]["accumulated"] += accumulated_time
            tree[current_activity_name]["data"]["time"]["remainder"] += remainder_time
            tree[current_activity_name]["data"]["time"]["max"] = max(
                tree[current_activity_name]["data"]["time"]["max"], activity_time
            )
            tree[current_activity_name]["data"]["time"]["min"] = min(
                tree[current_activity_name]["data"]["time"]["min"], activity_time
            )

        next_depth = depth + 1
        if next_depth < len(current_case["activities"]):
            tree[current_activity_name]["childrens"] = self.nest_activities(
                tree[current_activity_name]["childrens"], current_case, next_depth, case_data
            )
            return tree
        return tree

    def get_tree(self) -> dict:
        return self.tree
