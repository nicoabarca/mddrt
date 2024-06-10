import graphviz


class DirectlyRootedTreeDiagrammer:
    def __init__(
        self,
        tree: dict,
        visualize_frequency: bool = True,
        visualize_time: bool = True,
        visualize_cost: bool = True,
        visualize_rework: bool = True,
        visualize_flexibility: bool = True,
        rankdir: str = "TB",
    ) -> None:
        self.tree = tree
        self.visualiz_frequency = visualize_frequency
        self.visualize_time = visualize_time
        self.visualize_cost = visualize_cost
        self.visualize_rework = visualize_rework
        self.visualize_flexibility = visualize_flexibility
        self.rankdir = rankdir
        self.state_counter = 0
        self.diagram = graphviz.Digraph("mddrt", comment="Multi Dimension Directly Rooted Tree")
        self.build_diagram()

    def build_diagram(self):
        self.add_config()
        self.traverse_to_diagram()

    def add_config(self):
        self.diagram.graph_attr["rankdir"] = self.rankdir

    def traverse_to_diagram(self):
        # TODO: dont hard code this value, maybe use the names of start activities
        root_name = "Coordinate verification of polygon pits status"
        root = self.tree[root_name]
        self.dfs(root, root_name)
        # print(self.diagram.source)

    def dfs(self, node: dict, name: str):
        # State Node
        state_node_name = "s" + str(self.state_counter)
        self.state_counter += 1
        state_label = self.build_state_label(node, name)
        self.diagram.node(
            name=state_node_name,
            label=state_label,
            shape="none",
        )

        # Activity Node
        activity_node_name = str(node["data"]["id"])
        self.diagram.node(name=activity_node_name, label=f"{name} ({node['data']['frequency']})", shape="none")

        # Edge between Activity and State
        self.diagram.edge(activity_node_name, state_node_name)

        # print(f"Node ID: {node['data']['id']}, Path: {path}")

        if node["children"]:
            for child_name, child_node in node["children"].items():
                # Link between State and Node Children
                self.diagram.edge(state_node_name, str(child_node["data"]["id"]))
                # Keep traversing
                self.dfs(child_node, child_name)

    def build_state_label(self, node: dict, name: str):
        label_data = " "
        for dimension in node["data"].keys():
            if dimension in ["cost", "time"]:
                for data_name, measure in node["data"][dimension].items():
                    label_data += f"{data_name}: {measure}\n"
                label_data += "--------------\n"
        return label_data

    def state_label_data(self, node: dict, name: str):
        pass

    def build_activity_label(self, node: dict, name: str):
        pass

    def activity_label_data(self, node: dict, name: str):
        pass

    def get_diagram_string(self):
        return self.diagram.source
