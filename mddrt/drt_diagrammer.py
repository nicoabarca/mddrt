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
        self.state_counter = 1
        self.diagram = graphviz.Digraph("mddrt", comment="Multi Dimension Directly Rooted Tree")
        self.build_diagram()

    def build_diagram(self):
        self.add_config()
        # self.add_start_state()
        self.traverse_to_diagram()

    def add_config(self):
        self.diagram.graph_attr["rankdir"] = self.rankdir

    def add_start_state(self):
        tree_keys = list(self.tree.keys())
        start_state_dict = self.tree[tree_keys[0]]["data"].copy()
        breakpoint()
        start_state_dict["id"] = 0
        for dimension in tree_keys[1:]:  # TODO: fix this iterable
            if dimension == "frequency":
                start_state_dict[dimension] += self.tree["data"][dimension]
            if dimension in ["time", "cost", "flexibility", "quality"]:
                for data_name, measure in self.tree["data"][dimension].items():
                    if data_name == "max":
                        start_state_dict[dimension][data_name] = max(
                            start_state_dict[dimension][data_name],
                            measure,
                        )
                    elif data_name == "min":
                        start_state_dict[dimension][data_name] = min(
                            start_state_dict[dimension][data_name],
                            measure,
                        )
                    else:
                        start_state_dict[dimension][data_name] += measure

        breakpoint()

    def traverse_to_diagram(self):
        roots_names = self.tree.keys()
        for name in roots_names:
            root = self.tree[name]
            self.dfs(root, name)

    def dfs(self, node: dict, name: str):
        # State Node
        state_node_id = "s" + str(self.state_counter)
        self.state_counter += 1
        state_label = self.build_state_label(node, name)
        self.diagram.node(
            name=state_node_id,
            label=state_label,
            shape="none",
        )

        # Activity Node
        activity_node_id = str(node["data"]["id"])
        activity_label = self.build_activity_label(node, name)
        self.diagram.node(name=activity_node_id, label=activity_label, shape="none")

        # Edge between Activity and State
        self.diagram.edge(activity_node_id, state_node_id)

        if node["children"]:
            for child_name, child_node in node["children"].items():
                # Link between State and Node Children
                self.diagram.edge(state_node_id, str(child_node["data"]["id"]))
                # Keep traversing
                self.dfs(child_node, child_name)

    def build_state_label(self, node: dict, name: str):
        label_data = " "
        for dimension in node["data"].keys():
            if dimension in ["time", "cost", "flexibility", "quality"]:
                label_data += f"------{dimension}--------\n"
                for data_name, measure in node["data"][dimension].items():
                    if data_name not in ["max", "min", "statistic", "total"]:
                        if dimension == "time":
                            label_data += f"Avg. {data_name}: {measure}\n"
                        else:
                            label_data += f"Avg. {data_name}: {round(measure / node['data']['frequency'], 2)}\n"

        return label_data

    def state_label_data(self, node: dict, name: str):
        pass

    def build_activity_label(self, node: dict, name: str):
        label_data = f"{name} ({node['data']['frequency']})\n"
        for dimension in node["data"].keys():
            if dimension in ["time", "cost", "flexibility", "quality"]:
                label_data += f"------{dimension}--------\n"
                for data_name, measure in node["data"][dimension].items():
                    if data_name not in ["total_case", "remainder", "accumulated", "statistic"]:
                        if dimension == "time":
                            if data_name in ["min", "max"]:
                                label_data += f"{data_name} {dimension}: {measure}\n"
                            else:
                                label_data += f"Avg. {data_name}: {measure / node['data']['frequency']}\n"
                        elif data_name in ["min", "max"]:
                            label_data += f"{data_name} {dimension}: {measure}\n"
                        else:
                            label_data += f"Avg. {data_name}: {round(measure / node['data']['frequency'], 2)}\n"
        return label_data

    def activity_label_data(self, node: dict, name: str):
        pass

    def get_diagram_string(self):
        return self.diagram.source
