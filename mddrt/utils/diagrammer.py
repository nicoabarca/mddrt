from __future__ import annotations

from collections import deque
from datetime import timedelta
from typing import TYPE_CHECKING, Literal

from mddrt.utils.color_schemes import (
    COST_COLOR_SCHEME,
    FLEXIBILITY_COLOR_SCHEME,
    FREQUENCY_COLOR_SCHEME,
    QUALITY_COLOR_SCHEME,
    TIME_COLOR_SCHEME,
)

if TYPE_CHECKING:
    from mddrt.tree_node import TreeNode


def dimensions_min_and_max(tree_root: TreeNode) -> dict[str, list[int]]:
    dimensions_min_and_max = {"frequency": [0, 0]}
    for dimension in tree_root.dimensions_data:
        dimensions_min_and_max[dimension] = [0, 0]

    queue = deque([tree_root])

    while queue:
        current_node = queue.popleft()

        dimensions_min_and_max["frequency"][0] = min(dimensions_min_and_max["frequency"][0], current_node.frequency)
        dimensions_min_and_max["frequency"][1] = max(dimensions_min_and_max["frequency"][0], current_node.frequency)

        for dimension, data in current_node.dimensions_data.items():
            dimension_avg_total_case = (
                data["total_case"] / current_node.frequency
                if dimension != "time"
                else (data["lead_case"] / current_node.frequency).total_seconds()
            )
            dimensions_min_and_max[dimension][0] = min(dimensions_min_and_max[dimension][0], dimension_avg_total_case)
            dimensions_min_and_max[dimension][1] = max(dimensions_min_and_max[dimension][0], dimension_avg_total_case)

        for child in current_node.children:
            queue.append(child)

    return dimensions_min_and_max


def background_color(
    measure: timedelta | int,
    dimension: Literal["frequency", "cost", "time", "flexibility", "quality"],
    dimension_scale: tuple[int, int],
) -> str:
    if isinstance(measure, timedelta):
        measure = measure.total_seconds()
    color_scheme_range = (90, 255)
    color_scheme = color_scheme_by_dimension(dimension)
    assigned_color_index = interpolated_value(measure, dimension_scale, color_scheme_range)
    return color_scheme[assigned_color_index]


def interpolated_value(measure: int, from_scale: tuple[int, int], to_scale: tuple[int, int]) -> int:
    measure = max(min(measure, from_scale[1]), from_scale[0])
    denominator = max(1, (from_scale[1] - from_scale[0]))
    normalized_value = (measure - from_scale[0]) / denominator
    interpolated_value = to_scale[0] + normalized_value * (to_scale[1] - to_scale[0])
    return round(interpolated_value)


def color_scheme_by_dimension(dimension: Literal["frequency", "cost", "time", "flexibility", "quality"]) -> list[str]:
    dimension_color_schemes = {
        "frequency": FREQUENCY_COLOR_SCHEME,
        "cost": COST_COLOR_SCHEME,
        "time": TIME_COLOR_SCHEME,
        "flexibility": FLEXIBILITY_COLOR_SCHEME,
        "quality": QUALITY_COLOR_SCHEME,
    }
    return dimension_color_schemes.get(dimension)


def format_time(time: timedelta) -> str:
    years = round(time.days // 365)
    months = round((time.days % 365) // 30)
    days = round((time.days % 365) % 30)
    hours = round(time.seconds // 3600)
    minutes = round((time.seconds % 3600) // 60)
    seconds = round(time.seconds % 60)

    if years > 0:
        return f"{years:02d}y {months:02d}m {days:02d}d "
    if months > 0:
        return f"{months:02d}m {days:02d}d {hours:02d}h "
    if days > 0:
        return f"{days:02d}d {hours:02d}h {minutes:02d}m "
    if hours > 0:
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s "
    if minutes > 0:
        return f"{minutes:02d}m {seconds:02d}s"
    return f"{seconds:02d}s"


def dimensions_to_diagram(time: bool, cost: bool, quality: bool, flexibility: bool) -> list[str]:
    dimensions_to_diagram = []
    if time:
        dimensions_to_diagram.append("time")
    if cost:
        dimensions_to_diagram.append("cost")
    if quality:
        dimensions_to_diagram.append("quality")
    if flexibility:
        dimensions_to_diagram.append("flexibility")
    return dimensions_to_diagram


def link_width(measure: int, dimension_scale: list[int]) -> int:
    width_scale = (1, 8)
    return round(interpolated_value(measure, dimension_scale, width_scale), 2)
