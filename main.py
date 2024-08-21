import os
from itertools import combinations, product
from pathlib import Path

import pandas as pd

import mddrt

minimal_log_path = Path("data") / "minimal_log_4.csv"
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

cars_reparation_log_path = Path("data") / "reparacion_vehiculos_con_atributos.csv"
cars_reparation_event_log = pd.read_csv(cars_reparation_log_path, sep=";")
cars_reparation_format = {
    "case:concept:name": "ID Caso",
    "concept:name": "Actividad",
    "time:timestamp": "Fin",
    "start_timestamp": "Inicio",
    "org:resource": "",
    "cost:total": "",
}
cars_reparation_event_log = mddrt.log_formatter(cars_reparation_event_log, cars_reparation_format)

traffic_log_path = Path("data") / "Road_Traffic_Fine_Management_Process.csv"
traffic_event_log = pd.read_csv(traffic_log_path, sep=",")
traffic_format = {
    "case:concept:name": "Case ID",
    "concept:name": "Activity",
    "time:timestamp": "Complete Timestamp",
    "start_timestamp": "",
    "org:resource": "",
    "cost:total": "",
}
traffic_event_log = mddrt.log_formatter(traffic_event_log, traffic_format)

## Testing Purpose Only Code

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
for event_log in [blasting_event_log]:
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
                            format="pdf",
                        )
                        print(f"Diagramming: {file_name}")
