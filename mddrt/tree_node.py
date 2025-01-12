from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from mddrt.utils.builder import activities_dimension_cumsum, create_dimensions_data
from mddrt.utils.optional_activities import OptionalActivities
from mddrt.utils.misc import pretty_format_dict

if TYPE_CHECKING:
    from datetime import timedelta


class TreeNode:
    id: int = 0

    def __init__(self, name: str, depth: int) -> None:
        self.id: int = TreeNode.id
        self.name: str = name
        self.depth: int = depth
        self.frequency: int = 0
        self.dimensions_data: dict[Literal["cost", "time", "flexibility", "quality"], dict] = create_dimensions_data()
        self.parent: TreeNode = None
        self.children: list[TreeNode] = []
        TreeNode.id += 1

    def add_children(self, node: TreeNode) -> None:
        self.children.append(node)

    def set_parent(self, parent_node: TreeNode) -> None:
        self.parent = parent_node

    def get_child_by_name_and_depth(self, name: str, depth: int) -> TreeNode | None:
        for child in self.children:
            if child.name == name and child.depth == depth:
                return child
        return None

    def update_frequency(self) -> None:
        self.frequency += 1

    def update_dimension(self, dimension: str, depth: int, current_case: dict) -> None:
        update_methods = {
            "time": self.update_time_dimension,
            "cost": self.update_cost_dimension,
            "quality": self.update_quality_dimension,
            "flexibility": self.update_flexibility_dimension,
        }

        if dimension in update_methods:
            update_methods[dimension](depth, current_case)

    def update_time_dimension(self, depth: int, current_case: dict) -> None:
        time_data = self.dimensions_data["time"]
        activity = current_case["activities"][depth]

        service_time = activity["service_time"]
        waiting_time = activity["waiting_time"]
        lead_time = service_time + waiting_time
        lead_accumulated = activities_dimension_cumsum(current_case, "time")[depth]
        time_data["service"] += service_time
        time_data["waiting"] += waiting_time
        time_data["lead"] += lead_time
        time_data["lead_case"] += current_case["time"]
        time_data["lead_accumulated"] += lead_accumulated
        time_data["lead_remainder"] = time_data["lead_case"] - time_data["lead_accumulated"]
        self.update_min_max(time_data, service_time)

    def update_cost_dimension(self, depth: int, current_case: dict) -> None:
        dimension_data = self.dimensions_data["cost"]
        activity_cost = current_case["activities"][depth]["cost"]
        cost_cumsum = activities_dimension_cumsum(current_case, "cost")

        self.update_cumulative_data(dimension_data, activity_cost, cost_cumsum[depth], current_case["cost"])
        self.update_min_max(dimension_data, activity_cost)

    def update_quality_dimension(self, depth: int, current_case: dict) -> None:
        dimension_data = self.dimensions_data["quality"]
        activities_till_depth = [activity["name"] for activity in current_case["activities"]][: depth + 1]
        accumulated_rework = len(activities_till_depth) - len(set(activities_till_depth))
        self.update_cumulative_data(dimension_data, accumulated_rework, accumulated_rework, current_case["quality"])

    def update_flexibility_dimension(self, depth: int, current_case: dict) -> None:
        dimension_data = self.dimensions_data["flexibility"]
        case_activities = [activity["name"] for activity in current_case["activities"]]
        optional_activities = OptionalActivities().get_activities()
        activities_till_depth = case_activities[: depth + 1]
        accumulated_optionality = len(set(activities_till_depth) & set(optional_activities))
        self.update_cumulative_data(
            dimension_data, accumulated_optionality, accumulated_optionality, current_case["flexibility"]
        )

    def update_cumulative_data(
        self,
        dimension_data: dict,
        activity_value: float,
        dimension_cumsum: float,
        total_value: float,
    ) -> None:
        dimension_data["total"] += activity_value
        dimension_data["total_case"] += total_value
        dimension_data["accumulated"] += dimension_cumsum
        dimension_data["remainder"] = dimension_data["total_case"] - dimension_data["accumulated"]

    def update_min_max(self, dimension_data: dict, value_to_compare: float | timedelta) -> None:
        dimension_data["max"] = max(dimension_data["max"], value_to_compare)
        dimension_data["min"] = min(dimension_data["min"], value_to_compare)

    def __str__(self) -> str:
        return f"""
Id: {self.id}
Name: {self.name}
Depth: {self.depth}
Freq: {self.frequency}
Parent: {self.parent.name if self.parent else None} {self.parent.id if self.parent else None}
Data: \n{pretty_format_dict(self.dimensions_data)}
"""
