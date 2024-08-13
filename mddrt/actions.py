import shutil
import tempfile

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from graphviz import Source

from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.node.node import Node
from mddrt.tree_builder import DirectlyRootedTreeBuilder
from mddrt.tree_diagrammer import DirectlyRootedTreeDiagrammer
from mddrt.tree_grouper import DirectedRootedTreeGrouper
from mddrt.utils.actions import save_graphviz_diagram


def discover_multi_dimension_drt(
    log,
    calculate_time=True,
    calculate_cost=True,
    calculate_quality=True,
    calculate_flexibility=True,
    node_time_measures=["total"],  # ['total', 'consumed', 'remaining']
    node_cost_measures=["total"],  # ['total', 'consumed', 'remaining']
    arc_time_measures=["mean"],  # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    arc_cost_measures=["mean"],  # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    group_activities=False,  # si True, ejecutar función para agrupar secuencias de actividades sin caminos alternativos
    case_id_key="case:concept:name",
    activity_key="concept:name",
    timestamp_key="time:timestamp",
    start_timestamp_key="start_timestamp",
    cost_key="cost:total",
):
    parameters = DirectlyRootedTreeParameters(
        case_id_key,
        activity_key,
        timestamp_key,
        start_timestamp_key,
        cost_key,
        calculate_time,
        calculate_cost,
        calculate_quality,
        calculate_flexibility,
        node_time_measures,
        node_cost_measures,
        arc_time_measures,
        arc_cost_measures,
    )
    multi_dimension_drt = DirectlyRootedTreeBuilder(log, parameters).get_tree()
    if group_activities:
        multi_dimension_drt = group_drt_activities(multi_dimension_drt)

    return multi_dimension_drt


def group_drt_activities(multi_dimension_drt: Node):
    grouper = DirectedRootedTreeGrouper(multi_dimension_drt)
    return grouper.get_tree()


def group_log_activities(
    log,
    activities,  # lista con actividades a agrupar
    group_name="",
):  # nombre de la nueva 'actividad' que agrupa a las otras, si está en blanco, usar como nombre la lista de actividades
    # Agrupación manual de actividades del log, previo a la ejecución de discover_multi_dimension_drt

    # Cada actividad puede ocurrir N veces en cada ejecución del proceso. Se tendrían que crear de i=0 a N grupos, donde i es la ocurrencia i de cada actividad
    # En otras palabras, si queremos agrupar A y B en la traza ABCDBCAB, tendríamos como resultado algo como [AB]CD[AB]CB (la tercera B no se agrupa, pues no hay una tercera A)

    return log


def get_multi_dimension_drt_string(
    multi_dimension_drt: Node,
    visualize_time: bool = True,
    visualize_cost: bool = True,
    visualize_quality: bool = True,
    visualize_flexibility: bool = True,
):
    diagrammer = DirectlyRootedTreeDiagrammer(
        multi_dimension_drt,
        visualize_time=visualize_time,
        visualize_cost=visualize_cost,
        visualize_quality=visualize_quality,
        visualize_flexibility=visualize_flexibility,
    )
    drt_string = diagrammer.get_diagram_string()

    return drt_string


def view_multi_dimension_drt(
    multi_dimension_drt: Node,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    format="png",
):
    drt_string = get_multi_dimension_drt_string(
        multi_dimension_drt,
        visualize_time=visualize_time,
        visualize_cost=visualize_cost,
        visualize_quality=visualize_quality,
        visualize_flexibility=visualize_flexibility,
    )

    tmp_file = tempfile.NamedTemporaryFile(suffix=".gv")
    tmp_file.close()
    src = Source(drt_string, tmp_file.name, format=format)

    render = src.render(cleanup=True)
    shutil.copyfile(render, tmp_file.name)

    img = mpimg.imread(tmp_file.name)
    plt.axis("off")
    plt.tight_layout(pad=0, w_pad=0, h_pad=0)
    plt.imshow(img)
    plt.show()


def save_vis_dimension_drt(
    multi_dimension_drt,
    file_path,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    format="png",
):
    drt_string = get_multi_dimension_drt_string(
        multi_dimension_drt,
        visualize_time=visualize_time,
        visualize_cost=visualize_cost,
        visualize_quality=visualize_quality,
        visualize_flexibility=visualize_flexibility,
    )
    save_graphviz_diagram(drt_string, file_path, format)
