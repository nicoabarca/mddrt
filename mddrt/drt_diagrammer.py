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
        # FIX: dont hard code this value, maybe use the names of start activities
        root_name = "Coordinate verification of polygon pits status"
        root = self.tree[root_name]
        self.dfs(root, root_name)
        print(self.diagram.source)

    def dfs(self, node: dict, name: str, path=""):
        # TODO: add state node and add activity node
        # State Node
        state_node_id = "s" + str(self.state_counter)
        self.state_counter += 1
        self.diagram.node(
            state_node_id,
            label=f'{state_node_id} {str(node["data"]["cost"]["total_case"])}',
            shape="none",
        )

        # Activity Node
        activity_node_id = str(node["data"]["id"])
        self.diagram.node(activity_node_id, label=name, shape="none")

        # Edge between Activity and State
        self.diagram.edge(activity_node_id, state_node_id)

        print(f"Node ID: {node['data']['id']}, Path: {path}")

        if node["children"]:
            for child_name, child_node in node["children"].items():
                # Link between State and Node Children
                self.diagram.edge(state_node_id, str(child_node["data"]["id"]))
                # Keep traversing
                self.dfs(child_node, child_name, path + "/" + child_name)

    def get_diagram_string(self):
        return self.diagram.source
