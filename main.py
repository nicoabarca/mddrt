import os
from itertools import combinations, product
from pathlib import Path

import pandas as pd

import mddrt

minimal_log_path = Path("data") / "minimal_log_5.csv"
minimal_event_log = pd.read_csv(minimal_log_path, sep=";")
minimal_format = {
    "case:concept:name": "case",
    "concept:name": "activity",
    "time:timestamp": "complete",
    "start_timestamp": "",
    "org:resource": "",
    "cost:total": "cost",
}
minimal_event_log = mddrt.log_formatter(minimal_event_log, minimal_format)

bug_log_path = Path("data") / "Bug1.csv"
bug_event_log = pd.read_csv(bug_log_path, sep=",")
bug_format = {
    "case:concept:name": "Rut",
    "concept:name": "Actividad",
    "time:timestamp": "Timestamp",
    "start_timestamp": "",
    "org:resource": "PPS rango",
    "cost:total": "",
}
bug_event_log = mddrt.log_formatter(bug_event_log, bug_format, timestamp_format="mixed")


blasting_log_path = Path("data") / "blasting_with_rework_event_log.csv"
blasting_event_log = pd.read_csv(blasting_log_path, sep=";")
blasting_format = {
    "case:concept:name": "Case ID",
    "concept:name": "Activity",
    "time:timestamp": "Complete",
    "start_timestamp": "Start",
    "org:resource": "Resource",
    "cost:total": "Cost",
}
blasting_event_log = mddrt.log_formatter(blasting_event_log, blasting_format)

# TESTING CODE
drt = mddrt.discover_multi_dimensional_drt(minimal_event_log)
# mddrt.save_vis_multi_dimensional_drt(drt, file_path="blasting", format="svg")
mddrt.view_multi_dimensional_drt(
    drt, node_measures=["total", "consumed", "remaining"], arc_measures=["avg"], format="png"
)
breakpoint()

# Arc measures combinations without repeating
arc_measures = ["avg", "min", "max"]
all_combinations = []
for r in range(1, len(arc_measures) + 1):
    all_combinations.extend(combinations(arc_measures, r))
arc_measures_combinations = [list(combo) for combo in all_combinations]
arc_measures_combinations.append([])
# Node measures combinations without repeating
node_measures_combinations = [["total"], ["total", "consumed"], ["total", "consumed", "remaining"]]

options = [True, False]
number_of_diagram_combinations = 0
for event_log in [minimal_event_log]:
    drt_normal = mddrt.discover_multi_dimensional_drt(
        event_log,
        calculate_cost=True,
        calculate_time=True,
        calculate_flexibility=True,
        calculate_quality=True,
        group_activities=False,
    )
    drt_grouped = mddrt.discover_multi_dimensional_drt(
        event_log,
        calculate_cost=True,
        calculate_time=True,
        calculate_flexibility=True,
        calculate_quality=True,
        group_activities=True,
    )

    for drt in [drt_normal, drt_grouped]:
        for index, (visualize_cost, visualize_time, visualize_flexibility, visualize_quality) in enumerate(
            product(options, repeat=4),
        ):
            for i in range(8):  # 8 is the number of no repeating combinations of 3 elements + no elements
                arc_measures = arc_measures_combinations[i]
                for node_measures in node_measures_combinations:  # 3 options for node_measures
                    dimension_suffixes = [
                        "_cost_" if visualize_cost else "",
                        "_time_" if visualize_time else "",
                        "_flex_" if visualize_flexibility else "",
                        "_qual_" if visualize_quality else "",
                    ]

                    is_grouped_string = "_grouped_" if drt == drt_grouped else ""
                    file_name = f"{number_of_diagram_combinations}{is_grouped_string + ''.join(dimension_suffixes) + '_' + '_'.join(node_measures) + '_' + '_'.join(arc_measures)}"
                    number_of_diagram_combinations += 1

                    if any([visualize_cost, visualize_time, visualize_flexibility, visualize_quality]):
                        mddrt.save_vis_multi_dimensional_drt(
                            drt,
                            visualize_cost=visualize_cost,
                            visualize_time=visualize_time,
                            visualize_flexibility=visualize_flexibility,
                            visualize_quality=visualize_quality,
                            arc_measures=arc_measures,
                            node_measures=node_measures,
                            file_path=os.path.join("data", "diagrams", file_name),
                            format="svg",
                        )
                        print(f"Diagramming: {file_name}")
