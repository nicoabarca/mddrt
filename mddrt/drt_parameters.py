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
    # ['total', 'consumed', 'remaining']
    node_time_measures: list = field(default_factory=lambda: ["total"])
    # ['total', 'consumed', 'remaining']
    node_cost_measures: list = field(default_factory=lambda: ["total"])
    # rework y flexibility solo pueden ser medidas a nivel de todo el caso
    node_time_measure_aggregation: str = "mean"  # mean, median, sum, max, min, stdev
    node_cost_measure_aggregation: str = "mean"  # mean, median, sum, max, min, stdev
    node_rework_measure_aggregation: str = "mean"  # mean, median, sum, max, min, stdev
    node_flexibility_measure_aggregation: str = "mean"  # mean, median, sum, max, min, stdev
    # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    arc_time_measures: list = field(default_factory=lambda: ["mean"])
    # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    arc_cost_measures: list = field(default_factory=lambda: ["mean"])
    # rework y flexibility solo pueden ser medidas a nivel de todo el caso
