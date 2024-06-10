import os
import pandas as pd
import mddrt
import json

log_path = os.path.join("data", "blasting_with_rework_event_log.csv")

blasting_event_log = pd.read_csv(log_path, sep=";")

blasting_format = {
    "case:concept:name": "Case ID",
    "concept:name": "Activity",
    "time:timestamp": "Complete",
    "start_timestamp": "Start",
    "org:resource": "Resource",
    "cost:total": "Cost",
}

blasting_event_log = mddrt.log_formatter(blasting_event_log, blasting_format)
drt = mddrt.discover_multi_dimension_drt(blasting_event_log, calculate_time=False)
with open("data/tree.json", "w") as f:
    json_string = json.dumps(drt, indent=4)
    f.write(json_string)
mddrt.save_vis_dimension_drt(drt, file_path=os.path.join("data", "diagram"))
