from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.utils.builder import calculate_cases_metrics
import pandas as pd


class DirectlyRootedTreeBuilder:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log = log
        self.params = params
        self.tree = None
        self.cases = None
        self.build_tree()

    def build_tree(self) -> None:
        raw_cases_grouped_by_id = self.log.groupby(self.params.case_id_key, dropna=True, sort=False)
        self.build_cases(raw_cases_grouped_by_id)

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

    def build_case_activities(self, case: pd.DataFrame):
        case_activities = []
        for _, activity in case[1].iterrows():
            activity_dict = {}
            activity_dict["name"] = activity[self.params.activity_key]
            if self.params.calculate_cost:
                activity_dict["cost"] = activity[self.params.cost_key]
            if self.params.calculate_time:
                activity_dict["time"] = (
                    activity[self.params.timestamp_key] - activity[self.params.start_timestamp_key]
                )
            case_activities.append(activity_dict)
        return case_activities

    def get_tree(self) -> dict:
        return self.tree
