"""Module concerning plot layouts."""

import logging

from copy import deepcopy
from typing import Any

from embedding_visualization.parameters import PlotlyScatterParameters


logger: logging.Logger = logging.getLogger(__name__)


_BASE_LEGEND_CONFIG: dict[str, Any] = {
    "itemsizing": "constant",
    "xanchor": "left",
    "yanchor": "bottom",
    "y": 1.01,
    "orientation": "h",
    "font": {},
}


_BASE_AXIS_CONFIG: dict[str, Any] = {
    "linewidth": 2,
    "linecolor": "black",
    "showgrid": False,
    "zeroline": False,
    "showline": True,
    "mirror": True,
}


_BASE_SCENE_AXIS_CONFIG: dict[str, Any] = {
    "linewidth": 2,
    "linecolor": "#000000",
    "gridcolor": "#e3e3e3",
    "backgroundcolor": "#ffffff",
    "showgrid": True,
    "zeroline": True,
    "zerolinecolor": "#555555",
    "showline": True,
    "mirror": True,
}


_BASE_LAYOUT_CONFIG: dict[str, Any] = {
    "legend": _BASE_LEGEND_CONFIG,
    "xaxis": _BASE_AXIS_CONFIG,
    "yaxis": _BASE_AXIS_CONFIG,
    "scene": {
        "xaxis": _BASE_SCENE_AXIS_CONFIG,
        "yaxis": _BASE_SCENE_AXIS_CONFIG,
        "zaxis": _BASE_SCENE_AXIS_CONFIG,
    },
    "font": {},
    "plot_bgcolor": "rgba(0,0,0,0)",
}


def generate_layout(parameters: PlotlyScatterParameters) -> dict[str, Any]:
    """Generate plot layout.
    :param parameters: Plotly scatter parameters.
    :returns: Plot layout dictionary.
    """
    base_layout: dict[str, Any] = deepcopy(_BASE_LAYOUT_CONFIG)

    base_layout["title"] = parameters.title

    base_layout["font"]["size"] = parameters.layout_font_size

    base_layout["legend"]["font"]["size"] = parameters.legend_font_size

    if parameters.legend_position is not None:
        if parameters.legend_position == "top":
            base_layout["legend"]["yanchor"] = "bottom"
            base_layout["legend"]["y"] = 1.01
            base_layout["legend"]["orientation"] = "h"
        elif parameters.legend_position == "bottom":
            base_layout["legend"]["yanchor"] = "top"
            base_layout["legend"]["y"] = -0.1
            base_layout["legend"]["orientation"] = "h"
        elif parameters.legend_position == "left":
            base_layout["legend"]["xanchor"] = "right"
            base_layout["legend"]["x"] = -0.1
            base_layout["legend"]["y"] = 1.0
            base_layout["legend"]["yanchor"] = "top"
            base_layout["legend"]["orientation"] = "v"
        elif parameters.legend_position == "right":
            base_layout["legend"]["xanchor"] = "left"
            base_layout["legend"]["x"] = 1.01
            base_layout["legend"]["y"] = 1.0
            base_layout["legend"]["yanchor"] = "top"
            base_layout["legend"]["orientation"] = "v"
        else:
            raise ValueError(
                f"Invalid legend position: {parameters.legend_position}."
            )

    return base_layout
