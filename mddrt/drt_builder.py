import pandas as pd
from typing import Tuple
from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.utils.builder import (
    calculate_cases_metrics,
    get_start_activities,
    get_end_activities,
    create_case_data,
)


class DirectlyRootedTreeBuilder:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log = log
        self.params = params
        self.id_counter = 0
        self.tree = None
        self.cases = None
        self.start_activities = None
        self.end_activities = None
        self.build()

    def build(self) -> None:
        # TODO: order each case activity by initial timestamp and then order by end timestamp
        cases_grouped_by_id = self.log.groupby(self.params.case_id_key, dropna=True, sort=False)
        self.start_activities = get_start_activities(cases_grouped_by_id, self.params)
        self.end_activities = get_end_activities(cases_grouped_by_id, self.params)
        self.build_cases(cases_grouped_by_id)
        self.build_tree()

    def build_cases(self, cases_grouped_by_id: pd.Grouper) -> None:
        cases = {}
        cases_metrics = calculate_cases_metrics(self.log, self.params)
        for case in cases_grouped_by_id:
            case_id = case[0]
            cases[case_id] = {}
            case_activities = self.build_case_activities(case)
            case_metrics = cases_metrics.loc[cases_metrics["Case Id"] == case_id].iloc[0]
            cases[case_id]["activities"] = case_activities
            if self.params.calculate_cost:
                cases[case_id]["cost"] = int(case_metrics["Cost"])
            if self.params.calculate_time:
                cases[case_id]["time"] = case_metrics["Duration"]
            if self.params.calculate_flexibility:
                cases[case_id]["flexibility"] = int(case_metrics["Optionality"])
            if self.params.calculate_quality:
                cases[case_id]["quality"] = int(case_metrics["Rework"])
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

    def build_tree(self):
        tree = {}
        for _, current_case in self.cases.items():
            remainder_cost = 0
            remainder_time = 0
            remainder_flexibility = 0
            remainder_quality = 0
            if self.params.calculate_cost:
                remainder_cost = current_case["cost"]
            if self.params.calculate_time:
                remainder_time = current_case["time"]
            if self.params.calculate_flexibility:
                remainder_flexibility = current_case["flexibility"]
            if self.params.calculate_quality:
                remainder_quality = current_case["quality"]
            tree = self.nest_activities(
                tree=tree,
                current_case=current_case,
                depth=0,
                accumulated_cost=0,
                accumulated_time=pd.Timedelta(days=0),
                accumulated_flexibility=0,
                accumulated_quality=0,
                remainder_cost=remainder_cost,
                remainder_time=remainder_time,
                remainder_flexibility=remainder_flexibility,
                remainder_quality=remainder_quality,
            )
        self.tree = tree

    def nest_activities(
        self,
        tree: dict,
        current_case: dict,
        depth: int,
        accumulated_cost: int,
        accumulated_time: pd.Timedelta,
        accumulated_flexibility: int,
        accumulated_quality: int,
        remainder_cost: int,
        remainder_time: pd.Timedelta,
        remainder_flexibility: int,
        remainder_quality: int,
    ) -> dict:
        current_activity = current_case["activities"][depth]["name"]
        if tree.get(current_activity) is None:
            case_data = create_case_data(self.params, self.id_counter)
            tree[current_activity] = {"data": case_data, "children": dict()}
            self.id_counter += 1
        tree[current_activity]["data"]["frequency"] += 1

        if self.params.calculate_cost:
            activity_cost = current_case["activities"][depth]["cost"]

            accumulated_cost = accumulated_cost + activity_cost
            remainder_cost = remainder_cost - activity_cost

            tree[current_activity]["data"]["cost"]["total"] += activity_cost
            tree[current_activity]["data"]["cost"]["total_case"] += current_case["cost"]
            tree[current_activity]["data"]["cost"]["accumulated"] += accumulated_cost
            tree[current_activity]["data"]["cost"]["remainder"] += remainder_cost
            tree[current_activity]["data"]["cost"]["max"] = max(
                tree[current_activity]["data"]["cost"]["max"], activity_cost
            )
            tree[current_activity]["data"]["cost"]["min"] = min(
                tree[current_activity]["data"]["cost"]["min"], activity_cost
            )

        if self.params.calculate_time:
            activity_time = current_case["activities"][depth]["time"]
            accumulated_time = accumulated_time + activity_time
            remainder_time = remainder_time - activity_time

            tree[current_activity]["data"]["time"]["total"] += activity_time
            tree[current_activity]["data"]["time"]["total_case"] += current_case["time"]
            tree[current_activity]["data"]["time"]["accumulated"] += accumulated_time
            tree[current_activity]["data"]["time"]["remainder"] += remainder_time
            tree[current_activity]["data"]["time"]["max"] = max(
                tree[current_activity]["data"]["time"]["max"], activity_time
            )
            tree[current_activity]["data"]["time"]["min"] = min(
                tree[current_activity]["data"]["time"]["min"], activity_time
            )

        if self.params.calculate_flexibility:
            activity_flexibility = current_case["flexibility"] / len(current_case["activities"])
            accumulated_flexibility = accumulated_flexibility + activity_flexibility
            remainder_flexibility = remainder_flexibility - activity_flexibility

            tree[current_activity]["data"]["flexibility"]["total"] += activity_flexibility
            tree[current_activity]["data"]["flexibility"]["total_case"] += current_case["flexibility"]
            tree[current_activity]["data"]["flexibility"]["accumulated"] += accumulated_flexibility
            tree[current_activity]["data"]["flexibility"]["remainder"] += remainder_flexibility
            tree[current_activity]["data"]["flexibility"]["max"] = max(
                tree[current_activity]["data"]["flexibility"]["max"], current_case["flexibility"]
            )
            tree[current_activity]["data"]["flexibility"]["min"] = min(
                tree[current_activity]["data"]["flexibility"]["min"], current_case["flexibility"]
            )

        if self.params.calculate_quality:
            activity_quality = current_case["quality"] / len(current_case["activities"])
            accumulated_quality = accumulated_quality + activity_quality
            remainder_quality = remainder_quality - activity_quality

            tree[current_activity]["data"]["quality"]["total"] += activity_quality
            tree[current_activity]["data"]["quality"]["total_case"] += current_case["quality"]
            tree[current_activity]["data"]["quality"]["accumulated"] += accumulated_quality
            tree[current_activity]["data"]["quality"]["remainder"] += remainder_quality
            tree[current_activity]["data"]["quality"]["max"] = max(
                tree[current_activity]["data"]["quality"]["max"], current_case["quality"]
            )
            tree[current_activity]["data"]["quality"]["min"] = min(
                tree[current_activity]["data"]["quality"]["min"], current_case["quality"]
            )

        next_depth = depth + 1
        if next_depth < len(current_case["activities"]):
            tree[current_activity]["children"] = self.nest_activities(
                tree=tree[current_activity]["children"],
                current_case=current_case,
                depth=next_depth,
                accumulated_cost=accumulated_cost,
                accumulated_time=accumulated_time,
                accumulated_flexibility=accumulated_flexibility,
                accumulated_quality=accumulated_quality,
                remainder_cost=remainder_cost,
                remainder_time=remainder_time,
                remainder_flexibility=remainder_flexibility,
                remainder_quality=remainder_quality,
            )
        return tree

    def get_tree(self) -> dict:
        return self.tree
