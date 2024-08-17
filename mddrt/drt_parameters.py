from dataclasses import dataclass, field


@dataclass
class DirectlyRootedTreeParameters:
    case_id_key: str = "case:concept:name"
    activity_key: str = "concept:name"
    timestamp_key: str = "time:timestamp"
    start_timestamp_key: str = "start_timestamp"
    cost_key: str = "cost:total"
    calculate_time: bool = True
    calculate_cost: bool = True
    calculate_quality: bool = True
    calculate_flexibility: bool = True
    node_time_measures: list = field(default_factory=lambda: ["total"])
    node_cost_measures: list = field(default_factory=lambda: ["total"])
    arc_time_measures: list = field(default_factory=lambda: ["mean"])
    arc_cost_measures: list = field(default_factory=lambda: ["mean"])
