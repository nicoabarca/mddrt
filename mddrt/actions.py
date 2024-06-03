import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tempfile
import shutil
from graphviz import Source
from mddrt.utils.actions import save_graphviz_diagram
from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.drt_diagrammer import DirectlyRootedTreeDiagrammer
from mddrt.drt_builder import DirectlyRootedTreeBuilder


def discover_multi_dimension_drt(
    log,
    calculate_time=True,
    calculate_cost=True,
    calculate_rework=True,
    calculate_flexibility=True,
    node_time_measures=["total"],  # ['total', 'consumed', 'remaining']
    node_cost_measures=["total"],  # ['total', 'consumed', 'remaining']
    # rework y flexibility solo pueden ser medidas a nivel de todo el caso
    node_time_measure_aggregation="mean",  # mean, median, sum, max, min, stdev
    node_cost_measure_aggregation="mean",  # mean, median, sum, max, min, stdev
    node_rework_measure_aggregation="mean",  # mean, median, max, min, stdev
    node_flexibility_measure_aggregation="mean",  # mean, median, max, min, stdev
    arc_time_measures=["mean"],  # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    arc_cost_measures=["mean"],  # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    # rework y flexibility solo pueden ser medidas a nivel de todo el caso
    group_activities=False,  # si True, ejecutar función para agrupar secuencias de actividades sin caminos alternativos
    case_id_key="case:concept:name",
    activity_key="concept:name",
    timestamp_key="time:timestamp",
    start_timestamp_key="start_timestamp",
    cost_key="cost:total",
):
    # Ejemplo de output para el DRT generada con la versión actual de la herramienta
    # La nueva versión no tiene que ser exactamente igual, especialmente los nombres de los atributos se podrían refinar
    # La estructura se obtuvo con un código recursivo, pero no es necesario que la nueva versión lo sea

    parameters = DirectlyRootedTreeParameters(
        case_id_key,
        activity_key,
        timestamp_key,
        start_timestamp_key,
        cost_key,
        calculate_time,
        calculate_cost,
        calculate_rework,
        calculate_flexibility,
        node_time_measures,
        node_cost_measures,
        node_time_measure_aggregation,
        node_cost_measure_aggregation,
        node_rework_measure_aggregation,
        node_flexibility_measure_aggregation,
        arc_time_measures,
        arc_cost_measures,
    )
    multi_dimension_drt = DirectlyRootedTreeBuilder(log, parameters).get_tree()
    if group_activities:
        multi_dimension_drt = group_drt_activities(multi_dimension_drt)

    return multi_dimension_drt


def group_drt_activities(multi_dimension_drt):
    # Agrupación automática de secuencias de actividades sin caminos alternativos

    return multi_dimension_drt


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
    multi_dimension_drt: dict,
    visualize_time: bool = True,
    visualize_cost: bool = True,
    visualize_rework: bool = True,
    visualize_flexibility: bool = True,
):
    diagrammer = DirectlyRootedTreeDiagrammer(multi_dimension_drt)
    drt_string = diagrammer.get_diagram_string()

    return drt_string


def view_multi_dimension_drt(
    multi_dimension_drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_rework=True,
    visualize_flexibility=True,
    format="png",
):
    drt_string = get_multi_dimension_drt_string(multi_dimension_drt)

    tmp_file = tempfile.NamedTemporaryFile(suffix=".gv")
    tmp_file.close()
    src = Source(drt_string, tmp_file.name, format="png")

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
    visualize_rework=True,
    visualize_flexibility=True,
    format="png",
):
    drt_string = get_multi_dimension_drt_string(multi_dimension_drt)
    save_graphviz_diagram(drt_string, file_path, format)
