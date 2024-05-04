# En esta celda están las funciones que tendrían que ser implementadas, con sus input y output
from mddrt.drt_parameters import DirectlyRootedTreeParameters
from mddrt.drt import DirectlyRootedTree


def discover_multi_dimension_drt(
    log,
    calculate_time=True,
    calculate_cost=True,
    calculate_quality=True,
    calculate_flexibility=True,
    node_time_measures=["total"],  # ['total', 'consumed', 'remaining']
    node_cost_measures=["total"],  # ['total', 'consumed', 'remaining']
    # quality y flexibility solo pueden ser medidas a nivel de todo el caso
    node_time_measure_aggregation="mean",  # mean, median, sum, max, min, stdev
    node_cost_measure_aggregation="mean",  # mean, median, sum, max, min, stdev
    node_quality_measure_aggregation="mean",  # mean, median, sum, max, min, stdev
    node_flexibility_measure_aggregation="mean",  # mean, median, sum, max, min, stdev
    arc_time_measures=["mean"],  # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    arc_cost_measures=["mean"],  # ['mean', 'median', 'sum', 'max', 'min', 'stdev']
    # quality y flexibility solo pueden ser medidas a nivel de todo el caso
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
        calculate_quality,
        calculate_flexibility,
        node_time_measures,
        node_cost_measures,
        node_time_measure_aggregation,
        node_cost_measure_aggregation,
        node_quality_measure_aggregation,
        node_flexibility_measure_aggregation,
        arc_time_measures,
        arc_cost_measures,
    )
    drt = DirectlyRootedTree(log, parameters)

    multi_dimension_drt = {
        "A": {
            "cases": 2,
            "totalCost": 200,
            "maxCost": 100,
            "minCost": 100,
            "totalCaseCost": 500,
            "accumulatedCost": 200,
            "remainderCost": 300,
            "activities": {
                "A": {
                    "cases": 1,
                    "totalCost": 100,
                    "maxCost": 100,
                    "minCost": 100,
                    "totalCaseCost": 200,
                    "accumulatedCost": 200,
                    "remainderCost": 0,
                    "activities": {},
                },
                "B": {
                    "cases": 1,
                    "totalCost": 200,
                    "maxCost": 200,
                    "minCost": 200,
                    "totalCaseCost": 300,
                    "accumulatedCost": 300,
                    "remainderCost": 0,
                    "activities": {},
                },
            },
        }
    }

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
    multi_dimension_drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
):
    # Retornar String que pueda ser entregado a alguna de las funciones siguientes para visualizar/guardar, o que pueda ser entregado directamente a Graphviz

    return None


def view_multi_dimension_drt(
    multi_dimension_drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    format="png",
):  # png, svg, html (según viabilidad; si solo se puede PNG, es OK)
    string = get_multi_dimension_drt_string(multi_dimension_drt)

    # Visualizar diagrama

    return None


def save_vis_dimension_drt(
    multi_dimension_drt,
    file_path,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    format="png",
):  # png, svg, html (según viabilidad; si solo se puede PNG, es OK)
    string = get_multi_dimension_drt_string(multi_dimension_drt)

    # Guardar diagrama

    return None
