from typing import Dict, List, Literal, Union

from mddrt.utils.builder import activities_dimension_cumsum, create_dimensions_data
from mddrt.utils.misc import pretty_format_dict


class Node:
    id: int = 0

    def __init__(self, name: str, depth: int) -> None:
        self.id: int = Node.id
        self.name: str = name
        self.depth: int = depth
        self.frequency: int = 0
        self.dimensions_data: Dict[Literal["cost", "time", "flexibility", "quality"], dict] = create_dimensions_data()
        self.parent: Node = None
        self.children: List["Node"] = []
        Node.id += 1

    def add_children(self, node: "Node") -> None:
        self.children.append(node)

    def set_parent(self, parent_node: "Node") -> None:
        self.parent = parent_node

    def get_child_by_name_and_depth(self, name: str, depth: int) -> Union["Node", None]:
        for child in self.children:
            if child.name == name and child.depth == depth:
                return child

    def update_name(self, name: str) -> None:
        self.name = name

    def update_frequency(self) -> None:
        self.frequency += 1

    def update_dimensions_data(
        self,
        dimension: Literal["cost", "time", "flexibility", "quality"],
        depth: int,
        current_case: dict,
    ) -> None:
        dimension_to_update = self.dimensions_data[dimension]
        activity_dimension_value = (
            current_case["activities"][depth][dimension]
            if dimension in ["cost", "time"]
            else current_case[dimension] / len(current_case["activities"])
        )
        dimension_cumsum = activities_dimension_cumsum(current_case, dimension)

        dimension_to_update["total"] += activity_dimension_value
        dimension_to_update["total_case"] += current_case[dimension]
        dimension_to_update["accumulated"] += dimension_cumsum[depth]
        dimension_to_update["remainder"] = dimension_to_update["total_case"] - dimension_to_update["accumulated"]

        value_to_compare = None
        if dimension in ["cost", "time"]:
            value_to_compare = activity_dimension_value
        else:
            value_to_compare = current_case[dimension]

        dimension_to_update["max"] = max(dimension_to_update["max"], value_to_compare)
        dimension_to_update["min"] = min(dimension_to_update["min"], value_to_compare)

    def __str__(self) -> str:
        string = f"""
Id: {self.id}
Name: {self.name}
Depth: {self.depth}
Freq: {self.frequency}
Parent: {self.parent.name if self.parent else None} {self.parent.id if self.parent else None}
Data: \n{pretty_format_dict(self.dimensions_data)}
"""
        return string
