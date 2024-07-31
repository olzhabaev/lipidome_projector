"""Module concerning the generation of px scatter plots."""


from typing import Any, Literal

import pandas as pd
import plotly.express as px

from plotly.graph_objects import Figure

from embedding_visualization.figure_postprocessing import postprocess_figure
from embedding_visualization.layout import generate_layout
from embedding_visualization.marker_maps import (
    MarkerMaps,
)
from embedding_visualization.parameters import (
    PlotlyScatterParameters,
)
from embedding_visualization.scatter_data import ScatterData


def generate_px_scatter(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
    marker_maps: MarkerMaps,
) -> Figure:
    """Generate a plotly express scatter plot.
    :param scatter_data: Scatter data.
    :param parameters: Plotly parameters.
    :param marker_maps: Marker color and symbol maps.
    :returns: Plotly express scatter plot figure.
    """
    layout: dict[str, Any] = generate_layout(parameters)

    px_scatter_parameters: dict[str, Any] = _generate_px_scatter_param_dict(
        scatter_data,
        marker_maps,
        parameters,
        layout,
    )

    figure: Figure = _generate_scatter_px_figure(
        px_scatter_parameters, scatter_data.dimensionality
    )

    postprocess_figure(
        figure,
        scatter_data.hover_data_col_names,
        marker_maps.border_colormap,
        parameters.marker_sizeref,
        parameters.marker_sizemode,
        parameters.disable_hover,
        scatter_data.dimensionality,
    )

    return figure


def _generate_scatter_px_figure(
    px_scatter_parameters: dict[str, Any],
    dimensionality: Literal[2, 3],
) -> Figure:
    if dimensionality == 2:
        figure: Figure = px.scatter(**px_scatter_parameters)
    elif dimensionality == 3:
        figure: Figure = px.scatter_3d(**px_scatter_parameters)
    else:
        raise ValueError("Vector dimensionality may only be 2 or 3.")

    return figure


def _generate_px_scatter_param_dict(
    scatter_data: ScatterData,
    marker_maps: MarkerMaps,
    parameters: PlotlyScatterParameters,
    layout: dict[str, Any],
) -> dict[str, Any]:
    param_sub_dicts: list[dict[str, Any]] = []

    param_sub_dicts.append({"data_frame": scatter_data.dataframe})

    param_sub_dicts.append(
        _get_vector_column_parameters(scatter_data.vector_col_names)
    )

    param_sub_dicts.append(
        _get_marker_color_parameters(
            parameters.marker_colortype,
            scatter_data.color_column,
            marker_maps.colormap,
            marker_maps.colorscale,
            parameters.marker_opacity,
        )
    )

    param_sub_dicts.append(
        _get_marker_size_parameters(
            scatter_data.size_column,
            parameters.marker_sizemax,
        )
    )

    param_sub_dicts.append(
        _get_marker_symbol_parameters(
            scatter_data.symbol_column,
            marker_maps.symbol_map,
        )
    )

    param_sub_dicts.append(
        _get_custom_data_parameters(scatter_data.hover_data_col_names)
    )

    param_sub_dicts.append(_get_annotation_parameters(scatter_data))

    param_sub_dicts.append({"template": {"layout": layout}})

    param_sub_dicts.append(_get_figure_size_parameters(parameters.graph_size))

    px_scatter_param_dict: dict[str, Any] = _merge_sub_dicts(param_sub_dicts)

    return px_scatter_param_dict


def _get_annotation_parameters(scatter_data: ScatterData) -> dict[str, Any]:
    annotation_parameters: dict[str, Any] = {}

    if scatter_data.annotation_col_names is not None:
        annotations: pd.Series = scatter_data.dataframe[
            scatter_data.annotation_col_names
        ].apply(
            lambda row: "<br>".join(f"{value}" for value in row),
            axis=1,
        )
        annotation_parameters["text"] = annotations

    return annotation_parameters


def _get_custom_data_parameters(
    hover_data_column_names: list[str] | None,
) -> dict[str, Any]:
    custom_data_parameters: dict[str, Any] = {}

    if hover_data_column_names is not None:
        custom_data_parameters["custom_data"] = hover_data_column_names

    return custom_data_parameters


def _get_marker_symbol_parameters(
    symbol_column: pd.Series | None,
    symbol_map: dict[str, str] | dict[str, int] | None,
) -> dict[str, Any]:
    marker_symbol_parameters: dict[str, Any] = {}

    if symbol_column is not None:
        marker_symbol_parameters["symbol"] = symbol_column
        marker_symbol_parameters["symbol_map"] = symbol_map

    return marker_symbol_parameters


def _get_marker_color_parameters(
    color_type: Literal["discrete", "continuous"],
    color_column: pd.Series | None,
    colormap: dict[str, str] | None,
    colorscale: list[str] | None,
    marker_opacity: float,
) -> dict[str, Any]:
    marker_color_parameters: dict[str, Any] = {}

    if color_column is not None:
        marker_color_parameters["color"] = color_column

    if color_type == "discrete":
        marker_color_parameters["color_discrete_map"] = colormap
    elif color_type == "continuous":
        marker_color_parameters["color_continuous_scale"] = colorscale
    else:
        raise ValueError(f"Invalid color type: {color_type}")

    marker_color_parameters["opacity"] = marker_opacity

    return marker_color_parameters


def _get_marker_size_parameters(
    size_column: pd.Series | None,
    marker_size_max: float | None,
) -> dict[str, Any]:
    marker_size_parameters: dict[str, Any] = {}

    if size_column is not None:
        marker_size_parameters["size"] = size_column

    if marker_size_max is not None:
        marker_size_parameters["size_max"] = marker_size_max

    return marker_size_parameters


def _get_figure_size_parameters(graph_size: tuple[int, int]) -> dict[str, Any]:
    figure_size_parameters: dict[str, Any] = {}

    figure_size_parameters["width"] = graph_size[0]
    figure_size_parameters["height"] = graph_size[1]

    return figure_size_parameters


def _get_vector_column_parameters(
    vector_column_names: list[str],
) -> dict[str, Any]:
    vector_column_dict: dict[str, str] = dict(
        zip(["x", "y", "z"], vector_column_names)
    )

    return vector_column_dict


def _merge_sub_dicts(sub_dicts: list[dict[str, Any]]) -> dict[str, Any]:
    merged_dict: dict[str, Any] = {
        k: v for d in sub_dicts for k, v in d.items()
    }

    return merged_dict
