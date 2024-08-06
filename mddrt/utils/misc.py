import os
from collections import deque


def pretty_format_dict(d, indent=0):
    pretty_str = ""
    for key, value in d.items():
        pretty_str += "    " * indent + str(key) + ": "
        if isinstance(value, dict):
            pretty_str += "\n" + pretty_format_dict(value, indent + 1)
        elif isinstance(value, list):
            pretty_str += "[\n"
            for item in value:
                if isinstance(item, dict):
                    pretty_str += pretty_format_dict(item, indent + 1)
                else:
                    pretty_str += "    " * (indent + 1) + str(item) + "\n"
            pretty_str += "    " * indent + "]\n"
        else:
            pretty_str += str(value) + "\n"
    return pretty_str


def bfs(root, write_to_file=False):
    queue = deque([root])

    while queue:
        current_node = queue.popleft()
        if write_to_file:
            with open(os.path.join("data", "new_tree.txt"), "+a") as f:
                f.write(str(current_node))

        for child in current_node.children:
            queue.append(child)
