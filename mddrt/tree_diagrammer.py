from collections import deque
from typing import Callable, Literal

import graphviz

from mddrt.node.node import Node
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


class DirectlyRootedTreeDiagrammer:
    def __init__(
        self,
        tree_root: Node,
        visualize_time: bool = True,
        visualize_cost: bool = True,
        visualize_quality: bool = True,
        visualize_flexibility: bool = True,
        rankdir: str = "TB",
    ) -> None:
        self.tree_root = tree_root
        self.dimensions_to_diagram = dimensions_to_diagram(
            visualize_time, visualize_cost, visualize_quality, visualize_flexibility
        )
        self.rankdir = rankdir
        self.diagram = graphviz.Digraph("mddrt", comment="Multi Dimension Directly Rooted Tree")
        self.dimensions_min_and_max = dimensions_min_and_max(self.tree_root)
        self.build_diagram()

    def build_diagram(self) -> None:
        self.diagram.graph_attr["rankdir"] = self.rankdir
        self.traverse_to_diagram(self.build_node)
        self.traverse_to_diagram(self.build_links)

    def traverse_to_diagram(self, routine: Callable[[Node], None]) -> None:
        queue = deque([self.tree_root])

        while queue:
            current_node = queue.popleft()
            routine(current_node)
            for child in current_node.children:
                queue.append(child)

    def build_node(self, node: Node) -> None:
        state_label = self.build_state_label(node)
        self.diagram.node(str(node.id), label=f"<{state_label}>", shape="none")

    def build_links(self, node: Node) -> None:
        for child in node.children:
            link_label = self.build_link_label(child)
            penwidth = link_width(child.frequency, self.dimensions_min_and_max["frequency"])
            self.diagram.edge(
                tail_name=str(node.id), head_name=str(child.id), label=f"<{link_label}>", penwidth=str(penwidth)
            )

    def build_state_label(self, node: Node) -> str:
        content = ""
        for dimension in self.dimensions_to_diagram:
            content += self.build_state_row_string(dimension, node)
        return GRAPHVIZ_STATE_NODE.format(content)

    def build_state_row_string(self, dimension: Literal["cost", "time", "flexibility", "quality"], node: Node) -> str:
        avg_total_case = self.format_value("total_case", dimension, node)
        avg_consumed = self.format_value("accumulated", dimension, node)
        avg_remaining = self.format_value("remainder", dimension, node)
        dimension_row = f"{dimension.capitalize()}<br/>"
        dimension_row += (
            f"Avg. {'Lead' if dimension == 'time' else 'Total Case'} {dimension.capitalize()}: {avg_total_case}<br/>"
        )
        dimension_row += f"Avg. Consumed {dimension.capitalize()}: {avg_consumed}<br/>"
        dimension_row += f"Avg. Remaining {dimension.capitalize()}: {avg_remaining}<br/>"
        data = node.dimensions_data[dimension]
        bg_color = background_color(
            data["total_case"] / node.frequency, dimension, self.dimensions_min_and_max[dimension]
        )
        return GRAPHVIZ_STATE_NODE_ROW.format(bg_color, dimension_row)

    def build_link_label(self, node: Node) -> str:
        content = GRAPHVIZ_ACTIVITY_DATA.format(f"{node.name} ({node.frequency})")
        for dimension in self.dimensions_to_diagram:
            content += self.build_link_string(dimension, node)
        return GRAPHVIZ_ACTIVITY.format(content)

    def build_link_string(self, dimension: Literal["cost", "time", "flexibility", "quality"], node: Node) -> str:
        avg_total = self.format_value("total", dimension, node)
        maximum = self.format_value("max", dimension, node)
        minimum = self.format_value("min", dimension, node)
        link_row = f"{'Service' if dimension == 'time' else ''} {dimension.capitalize()}<br/>"
        link_row += f"Avg: {avg_total}<br/>"
        link_row += f"Max: {maximum}<br/>"
        link_row += f"Min: {minimum}<br/>"
        return GRAPHVIZ_ACTIVITY_DATA.format(link_row)

    def format_value(
        self,
        metric: Literal["total", "total_case", "accumulated", "remainder", "max", "min"],
        dimension: Literal["cost", "time", "flexibility", "quality"],
        node: Node,
    ) -> str:
        value = None

        if metric in ["total", "total_case", "accumulated", "remainder"]:
            value = node.dimensions_data[dimension][metric] / node.frequency
        else:
            value = node.dimensions_data[dimension][metric]

        if dimension == "time":
            return format_time(value)
        elif dimension == "cost":
            return f"{abs(round(value, 2))} USD"

        return abs(round(value, 2))

    def get_diagram_string(self) -> str:
        return self.diagram.source
