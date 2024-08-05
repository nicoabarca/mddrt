from typing import List
from mddrt.node.node import Node
from datetime import timedelta


class DirectedRootedTreeGrouper:
    def __init__(self, tree: Node) -> None:
        self.tree = tree
        self.start_group()

    def start_group(self):
        for child in self.tree.children:
            self.traverse_to_group(child)

    def traverse_to_group(self, node: Node) -> None:
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

    def group_nodes(self, parent_node: Node, nodes: List[Node]) -> Node:
        new_node = Node(f"From {nodes[0].name} to {nodes[-1].name}", nodes[0].depth)
        self.group_dimensions_data_in_new_node(new_node, nodes)
        first_node_index = parent_node.children.index(nodes[0])
        parent_node.children[first_node_index] = new_node
        new_node.children = nodes[-1].children

    def group_dimensions_data_in_new_node(self, grouped_node: Node, nodes: List[Node]):
        grouped_node.frequency = nodes[0].frequency
        for dimension in nodes[0].dimensions_data.keys():
            default = 0 if dimension != "time" else timedelta()
            for metric in ["total", "total_case", "accumulated", "remainder"]:
                grouped_node.dimensions_data[dimension][metric] = sum(
                    [node.dimensions_data[dimension][metric] for node in nodes], default
                )
            grouped_node.dimensions_data[dimension]["min"] = min(
                node.dimensions_data[dimension]["min"] for node in nodes
            )
            grouped_node.dimensions_data[dimension]["max"] = max(
                node.dimensions_data[dimension]["max"] for node in nodes
            )

    def get_tree(self) -> Node:
        return self.tree
