# Multi-Dimensional DRT Visualizer
This Python package allows users to visualize Directly-Rooted Trees (DRTs) that represent various dimensions of data derived from event logs. It provides tools to create graphical representations of these multi-dimensional trees, enabling deeper insights into process behaviors and relationships. The diagrams are generated via [Graphviz](https://www.graphviz.org).


# Installation
This package runs under Python 3.9+, use [pip](https://pip.pypa.io/en/stable/) to install.
```sh
pip install mddrt
```
To render and save generated diagrams, you will also need to install [Graphviz](https://www.graphviz.org)

# Quickstart

### Format event log
Using `mddrt.log_formatter` you can format your own initial event log with the corresponding column names based on [pm4py](https://pm4py.fit.fraunhofer.de) standard way of naming logs columns.

The format dictionary to pass as argument to this function needs to have the following structure:
```py
{
    "case:concept:name": <Case Id>, # required
    "concept:name": <Activity Id>, # required
    "time:timestamp": <Timestamp>, # required
    "start_timestamp": <Start Timestamp>, # optional
    "org:resource": <Resource>, # optional
    "cost:total": <Cost>, # optional
}
```

Each value of the dictionary needs to match the corresponding column name of the initial event log. If `start_timestamp`, `org:resource` and `cost:total` are not present in your event log, you can leave its values as blank strings.

```py
import mddrt
import pandas as pd

raw_event_log = pd.read_csv("raw_event_log.csv")

format_dictionary = {
    "case:concept:name": "Case ID",
    "concept:name": "Activity",
    "time:timestamp": "Complete",
    "start_timestamp": "Start",
    "org:resource": "Resource",
    "cost:total": "Cost",
}

event_log = mddrt.log_formatter(raw_event_log, format_dictionary)

```
### Discover Multi Dimension DRT

```py
drt = mddrt.discover_multi_dimensional_drt(
    event_log,
    calculate_cost=True,
    calculate_time=True,
    calculate_flexibility=True,
    calculate_quality=True,
    group_activities=False,
)
```

### Automatic group of activities 
```py
grouped_drt = mddrt.group_drt_activities(drt)
```

### Get the DRT diagram string representation
```py
mddrt_string = mpdfg.get_multi_dimension_drt_string(
    multi_dimension_drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True
)
```

### View the generated DRT diagram
Allows the user to view the diagram in interactive Python environments like Jupyter and Google Colab.

```py
mpdfg.view_multi_dimensional_drt(
    multi_dimensional_drt
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
)
```
### Save the generated DRT diagram

```py
mpdfg.save_vis_multi_dimensional_drt(
    multi_dimensional_drt
    file_path="diagram",
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    format="png", # or pdf, webp, svg, etc.
)
```

# Examples

Checkout [Examples](https://github.com/nicoabarca/mddrt/blob/main/examples) to see the package being used to visualize an event log of a mining process.