import os
import pandas as pd
import mddrt
import json

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

drt = mddrt.discover_multi_dimension_drt(
    blasting_event_log,
    calculate_cost=True,
    calculate_time=True,
    calculate_flexibility=True,
    calculate_quality=True,
)
# with open("data/tree.json", "w") as f:
#     json_string = json.dumps(drt, indent=2)
#     f.write(json_string)
mddrt.save_vis_dimension_drt(drt, file_path=os.path.join("data", "diagram"))
