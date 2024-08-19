from dataclasses import dataclass


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
