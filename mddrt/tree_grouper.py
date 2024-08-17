from __future__ import annotations

from datetime import timedelta

from mddrt.tree_node import TreeNode


class DirectedRootedTreeGrouper:
    def __init__(self, tree: TreeNode) -> None:
        self.tree: TreeNode = tree
        self.start_group()

    def start_group(self) -> None:
        for child in self.tree.children:
            self.traverse_to_group(child)

    def traverse_to_group(self, node: TreeNode) -> None:
        nodes_to_group = self.collect_nodes_to_group(node)

        if nodes_to_group:
            self.group_nodes(node.parent, nodes_to_group)

        for child in node.children:
            self.traverse_to_group(child)

    def collect_nodes_to_group(self, node: TreeNode) -> list[TreeNode]:
        nodes_to_group = []
        current_node = node

        while self.has_single_child(current_node):
            nodes_to_group.append(current_node)
            current_node = current_node.children[0]

        if nodes_to_group:
            nodes_to_group.append(current_node)

        return nodes_to_group

    def has_single_child(self, node: TreeNode) -> bool:
        return len(node.children) == 1

    def group_nodes(self, parent_node: TreeNode, nodes: list[TreeNode]) -> None:
        new_node_name = self.create_new_node_name(nodes)
        new_node = TreeNode(new_node_name, nodes[0].depth)

        self.group_dimensions_data_in_new_node(new_node, nodes)
        self.replace_old_nodes_with_new(parent_node, new_node, nodes)

    def create_new_node_name(self, nodes: list[TreeNode]) -> str:
        return f"From {nodes[0].name} to {nodes[-1].name}"

    def replace_old_nodes_with_new(self, parent_node: TreeNode, new_node: TreeNode, nodes: list[TreeNode]) -> None:
        first_node_index = parent_node.children.index(nodes[0])
        parent_node.children[first_node_index] = new_node
        new_node.children = nodes[-1].children
        new_node.set_parent(parent_node)

    def group_dimensions_data_in_new_node(self, grouped_node: TreeNode, nodes: list[TreeNode]) -> None:
        first_node = nodes[0]
        last_node = nodes[-1]

        grouped_node.frequency = first_node.frequency

        for dimension, data in first_node.dimensions_data.items():
            if dimension == "time":
                self.group_time_dimension_in_new_node(grouped_node, nodes)
                continue
            grouped_data = grouped_node.dimensions_data[dimension]

            grouped_data["total_case"] = data["total_case"]
            grouped_data["accumulated"] = last_node.dimensions_data[dimension]["accumulated"]
            grouped_data["remainder"] = last_node.dimensions_data[dimension]["remainder"]

            grouped_data["total"] = self.calculate_total(nodes, dimension)
            grouped_data["min"] = self.calculate_min(nodes, dimension)
            grouped_data["max"] = self.calculate_max(nodes, dimension)

    def group_time_dimension_in_new_node(self, grouped_node: TreeNode, nodes: list[TreeNode]) -> None:
        first_node = nodes[0]
        last_node = nodes[-1]

        grouped_data = grouped_node.dimensions_data["time"]
        grouped_data["lead_case"] = first_node.dimensions_data["time"]["lead_case"]
        grouped_data["lead_accumulated"] = last_node.dimensions_data["time"]["lead_accumulated"]
        grouped_data["lead_remainder"] = last_node.dimensions_data["time"]["lead_remainder"]

        grouped_data["lead"] = self.calculate_total(nodes, "time")
        grouped_data["min"] = self.calculate_min(nodes, "time")
        grouped_data["max"] = self.calculate_max(nodes, "time")

        grouped_data["service"] = sum([node.dimensions_data["time"]["service"] for node in nodes], timedelta())
        grouped_data["waiting"] = sum([node.dimensions_data["time"]["waiting"] for node in nodes], timedelta())

    def calculate_total(self, nodes: list[TreeNode], dimension: str) -> int | float | timedelta:
        if dimension == "time":
            return sum([node.dimensions_data["time"]["lead"] for node in nodes], timedelta())
        return sum(node.dimensions_data[dimension]["total"] for node in nodes)

    def calculate_min(self, nodes: list[TreeNode], dimension: str) -> int | float | timedelta:
        return min(node.dimensions_data[dimension]["min"] for node in nodes)

    def calculate_max(self, nodes: list[TreeNode], dimension: str) -> int | float | timedelta:
        return max(node.dimensions_data[dimension]["max"] for node in nodes)

    def get_tree(self) -> TreeNode:
        return self.tree
