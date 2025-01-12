import pandas as pd
import pm4py

from mddrt.tree_node import TreeNode


def prune_tree_to_depth(node: TreeNode, max_depth: int) -> None:
    """
    Prunes the tree to the specified maximum depth.

    Args:
        node (TreeNode): The root node of the tree to prune.
        max_depth (int): The maximum depth to retain in the tree.
    """
    if node.depth >= max_depth - 1:
        node.children = []
    else:
        for child in node.children:
            prune_tree_to_depth(child, max_depth)


def prune_log_based_on_top_variants(
    log: pd.DataFrame,
    k: int,
    activity_key="concept:name",
    timestamp_key="time:timestamp",
    case_id_key="case:concept:name",
) -> pd.DataFrame:
    """
    Prunes the event log to retain only the top k variants.

    This function filters the event log to keep only the top k variants based on their frequency.
    Variants are different sequences of activities in the event log.

    Args:
        log (pd.DataFrame): The event log data to prune, typically a DataFrame or similar structure.
        k (int): The number of top variants to retain in the pruned log.
        activity_key (str, optional): The key for activity names in the event log. Defaults to "concept:name".
        timestamp_key (str, optional): The key for timestamps in the event log. Defaults to "time:timestamp".
        case_id_key (str, optional): The key for case IDs in the event log. Defaults to "case:concept:name".

    Returns:
        pd.DataFrame: The pruned event log containing only the top k variants.
    """
    return pm4py.filter_variants_top_k(log, k, activity_key, timestamp_key, case_id_key)
