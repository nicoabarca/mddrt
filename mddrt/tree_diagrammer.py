from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Callable, Literal

import graphviz

from mddrt.utils.constants import (
    GRAPHVIZ_ACTIVITY,
    GRAPHVIZ_ACTIVITY_DATA,
    GRAPHVIZ_STATE_NODE,
    GRAPHVIZ_STATE_NODE_ROW,
)
from mddrt.utils.diagrammer import (
    background_color,
    dimensions_min_and_max,
    dimensions_to_diagram,
    format_time,
    link_width,
)

if TYPE_CHECKING:
    from datetime import timedelta

    from mddrt.tree_node import TreeNode

METRIC = Literal[
    "total",
    "total_case",
    "remainder",
    "accumulated",
    "max",
    "min",
    "lead",
    "lead_case",
    "lead_remainder",
    "lead_accumulated",
    "service",
    "waiting",
]


class DirectlyRootedTreeDiagrammer:
    def __init__(
        self,
        tree_root: TreeNode,
        visualize_time: bool = True,
        visualize_cost: bool = True,
        visualize_quality: bool = True,
        visualize_flexibility: bool = True,
        rankdir: str = "TB",
    ) -> None:
        self.tree_root = tree_root
        self.dimensions_to_diagram = dimensions_to_diagram(
            visualize_time,
            visualize_cost,
            visualize_quality,
            visualize_flexibility,
        )
        self.rankdir = rankdir
        self.diagram = graphviz.Digraph("mddrt", comment="Multi Dimension Directly Rooted Tree")
        self.dimensions_min_and_max = dimensions_min_and_max(self.tree_root)
        self.build_diagram()

    def build_diagram(self) -> None:
        self.diagram.graph_attr["rankdir"] = self.rankdir
        self.traverse_to_diagram(self.build_node)
        self.traverse_to_diagram(self.build_links)

    def traverse_to_diagram(self, diagram_routine: Callable[[TreeNode], None]) -> None:
        queue = deque([self.tree_root])

        while queue:
            current_node = queue.popleft()
            diagram_routine(current_node)
            for child in current_node.children:
                queue.append(child)

    def build_node(self, node: TreeNode) -> None:
        state_label = self.build_state_label(node)
        self.diagram.node(str(node.id), label=f"<{state_label}>", shape="none")

    def build_state_label(self, node: TreeNode) -> str:
        content = ""
        for dimension in self.dimensions_to_diagram:
            content += self.build_state_row_string(dimension, node)
        return GRAPHVIZ_STATE_NODE.format(content)

    def build_state_row_string(
        self,
        dimension: Literal["cost", "time", "flexibility", "quality"],
        node: TreeNode,
    ) -> str:
        avg_total_case = (
            self.format_value("total_case", dimension, node)
            if dimension != "time"
            else self.format_value("lead_case", dimension, node)
        )
        avg_consumed = (
            self.format_value("accumulated", dimension, node)
            if dimension != "time"
            else self.format_value("lead_accumulated", dimension, node)
        )
        avg_remaining = (
            self.format_value("remainder", dimension, node)
            if dimension != "time"
            else self.format_value("lead_remainder", dimension, node)
        )
        dimension_row = f"{dimension.capitalize()}<br/>"
        dimension_row += (
            f"Avg. {'Lead' if dimension == 'time' else 'Total Case'} {dimension.capitalize()}: {avg_total_case}<br/>"
        )
        dimension_row += f"Avg. Consumed {dimension.capitalize()}: {avg_consumed}<br/>"
        dimension_row += f"Avg. Remaining {dimension.capitalize()}: {avg_remaining}<br/>"
        data = node.dimensions_data[dimension]
        bg_color = background_color(
            (data["total_case"] if dimension != "time" else data["lead_case"]) / node.frequency,
            dimension,
            self.dimensions_min_and_max[dimension],
        )
        return GRAPHVIZ_STATE_NODE_ROW.format(bg_color, dimension_row)

    def build_links(self, node: TreeNode) -> None:
        for child in node.children:
            link_label = self.build_link_label(child)
            penwidth = link_width(child.frequency, self.dimensions_min_and_max["frequency"])
            self.diagram.edge(
                tail_name=str(node.id),
                head_name=str(child.id),
                label=f"<{link_label}>",
                penwidth=str(penwidth),
            )

    def build_link_label(self, node: TreeNode) -> str:
        content = GRAPHVIZ_ACTIVITY_DATA.format(f"{node.name} ({node.frequency})")
        for dimension in self.dimensions_to_diagram:
            content += self.build_link_string(dimension, node)
        return GRAPHVIZ_ACTIVITY.format(content)

    def build_link_string(
        self,
        dimension: Literal["cost", "time", "flexibility", "quality"],
        node: TreeNode,
    ) -> str:
        avg_total = (
            self.format_value("total", dimension, node)
            if dimension != "time"
            else self.format_value("lead", dimension, node)
        )
        maximum = self.format_value("max", dimension, node)
        minimum = self.format_value("min", dimension, node)
        link_row = f"{'Service' if dimension == 'time' else ''} {dimension.capitalize()}<br/>"
        link_row += f"Avg: {avg_total}<br/>"
        link_row += f"Max: {maximum}<br/>"
        link_row += f"Min: {minimum}<br/>"
        return GRAPHVIZ_ACTIVITY_DATA.format(link_row)

    def format_value(
        self,
        metric: METRIC,
        dimension: Literal["cost", "time", "flexibility", "quality"],
        node: TreeNode,
    ) -> str:
        value = self.get_dimension_metric_value(node, metric, dimension)
        return self.format_by_dimension(value, dimension)

    def get_dimension_metric_value(self, node: TreeNode, metric: METRIC, dimension: str) -> int | float | timedelta:
        if metric in ["max", "min"]:
            return node.dimensions_data[dimension][metric]
        return node.dimensions_data[dimension][metric] / node.frequency

    def format_by_dimension(self, value: float | timedelta, dimension: str) -> str:
        if dimension == "time":
            return format_time(value)
        if dimension == "cost":
            return f"{abs(round(value,2))} USD"
        return str(abs(round(value, 2)))

    def get_diagram_string(self) -> str:
        return self.diagram.source
