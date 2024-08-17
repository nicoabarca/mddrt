from datetime import timedelta
from typing import List

from mddrt.tree_node import TreeNode


class DirectedRootedTreeGrouper:
    def __init__(self, tree: TreeNode) -> None:
        self.tree: TreeNode = tree
        self.start_group()

    def start_group(self) -> None:
        for child in self.tree.children:
            self.traverse_to_group(child)

    def traverse_to_group(self, node: TreeNode) -> None:
        start_node = node
        actual_node = node
        nodes_to_group = []

        while len(actual_node.children) == 1:
            nodes_to_group.append(actual_node)
            actual_node = actual_node.children[0]

        if nodes_to_group:
            nodes_to_group.append(actual_node)
            self.group_nodes(start_node.parent, nodes_to_group)

        for child in actual_node.children:
            self.traverse_to_group(child)

    def group_nodes(self, parent_node: TreeNode, nodes: List[TreeNode]) -> None:
        new_node = TreeNode(f"From {nodes[0].name} to {nodes[-1].name}", nodes[0].depth)
        self.group_dimensions_data_in_new_node(new_node, nodes)
        first_node_index = parent_node.children.index(nodes[0])
        parent_node.children[first_node_index] = new_node
        new_node.children = nodes[-1].children

    def group_dimensions_data_in_new_node(self, grouped_node: TreeNode, nodes: List[TreeNode]) -> None:
        first_node = nodes[0]
        last_node = nodes[-1]

        grouped_node.frequency = first_node.frequency

        for dimension, data in first_node.dimensions_data.items():
            grouped_data = grouped_node.dimensions_data[dimension]

            grouped_data["total_case"] = data["total_case"]
            grouped_data["accumulated"] = last_node.dimensions_data[dimension]["accumulated"]
            grouped_data["remainder"] = last_node.dimensions_data[dimension]["remainder"]

            grouped_data["total"] = self.calculate_total(nodes, dimension)
            grouped_data["min"] = self.calculate_min(nodes, dimension)
            grouped_data["max"] = self.calculate_max(nodes, dimension)

    def calculate_total(self, nodes: List[TreeNode], dimension: str) -> float:
        default_zero = 0 if dimension != "time" else timedelta()
        return sum(node.dimensions_data[dimension]["total"] for node in nodes) or default_zero

    def calculate_min(self, nodes: List[TreeNode], dimension: str) -> float:
        return min(node.dimensions_data[dimension]["min"] for node in nodes)

    def calculate_max(self, nodes: List[TreeNode], dimension: str) -> float:
        return max(node.dimensions_data[dimension]["max"] for node in nodes)

    def get_tree(self) -> TreeNode:
        return self.tree
