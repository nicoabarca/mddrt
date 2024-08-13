import os
from itertools import product

import pandas as pd

import mddrt

blasting_log_path = os.path.join("data", "blasting_with_rework_event_log.csv")
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

cars_reparation_log_path = os.path.join("data", "reparacion_vehiculos_con_atributos.csv")
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

traffic_log_path = os.path.join("data", "Road_Traffic_Fine_Management_Process.csv")
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

drt_normal = mddrt.discover_multi_dimension_drt(
    blasting_event_log,
    calculate_cost=True,
    calculate_time=True,
    calculate_flexibility=True,
    calculate_quality=True,
    group_activities=False,
)

drt_grouped = mddrt.discover_multi_dimension_drt(
    blasting_event_log,
    calculate_cost=True,
    calculate_time=True,
    calculate_flexibility=True,
    calculate_quality=True,
    group_activities=True,
)


options = [True, False]

for index, (visualize_cost, visualize_time, visualize_flexibility, visualize_quality) in enumerate(
    product(options, repeat=4)
):
    suffixes = [
        "_cost_" if visualize_cost else "",
        "_time_" if visualize_time else "",
        "_flex_" if visualize_flexibility else "",
        "_qual_" if visualize_quality else "",
    ]

    file_name = f"{index}{''.join(suffixes)}"
    if any([visualize_cost, visualize_time, visualize_flexibility, visualize_quality]):
        mddrt.save_vis_dimension_drt(
            drt_normal,
            visualize_cost=visualize_cost,
            visualize_time=visualize_time,
            visualize_flexibility=visualize_flexibility,
            visualize_quality=visualize_quality,
            file_path=os.path.join("data", "diagrams_normal", file_name),
        )
        print(f"Diagramming normal: {index}")

for index, (visualize_cost, visualize_time, visualize_flexibility, visualize_quality) in enumerate(
    product(options, repeat=4)
):
    suffixes = [
        "_cost_" if visualize_cost else "",
        "_time_" if visualize_time else "",
        "_flex_" if visualize_flexibility else "",
        "_qual_" if visualize_quality else "",
    ]

    file_name = f"{index}{''.join(suffixes)}"

    if any([visualize_cost, visualize_time, visualize_flexibility, visualize_quality]):
        mddrt.save_vis_dimension_drt(
            drt_grouped,
            visualize_cost=visualize_cost,
            visualize_time=visualize_time,
            visualize_flexibility=visualize_flexibility,
            visualize_quality=visualize_quality,
            file_path=os.path.join("data", "diagrams_grouped", file_name),
        )
        print(f"Diagramming grouped: {index}")
