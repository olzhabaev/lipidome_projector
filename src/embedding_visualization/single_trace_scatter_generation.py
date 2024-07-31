"""Module concerning the generation of single trace Plotly scatterplots."""

import logging

from itertools import product
from typing import Any, cast, Literal

import pandas as pd

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


logger: logging.Logger = logging.getLogger(__name__)


def generate_single_trace_plotly_scatter(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
    marker_maps: MarkerMaps,
) -> Figure:
    """Generate a plotly scatter plot by creating a single trace
    within which all scatter marker attributes are set manually.
    :param scatter_data: Scatter data.
    :param parameters: Plotly parameters.
    :param marker_maps: Marker color and symbol maps.
    :returns: Plotly scatter plot figure.
    """
    layout: dict[str, Any] = _generate_tracewise_layout(
        scatter_data, parameters
    )

    figure: Figure = Figure(layout=layout)

    trace: dict[str, Any] = _generate_trace(
        scatter_data, parameters, marker_maps
    )

    figure.add_trace(trace)

    dummy_traces: list[dict[str, Any]] = (
        _generate_dummy_traces(scatter_data, marker_maps, parameters)
        if parameters.legend_type == "normal"
        else _generate_grouped_dummy_traces(
            scatter_data, marker_maps, parameters
        )
    )

    figure.add_traces(dummy_traces)

    postprocess_figure(
        figure=figure,
        hover_data_column_names=None,
        border_colormap=None,
        marker_sizeref=None,
        marker_sizemode=None,
        disable_hover=parameters.disable_hover,
        dimensionality=scatter_data.dimensionality,
    )

    return figure


def _generate_trace(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
    marker_maps: MarkerMaps,
) -> dict[str, Any]:
    sorted_scatter_df: pd.DataFrame = _get_sorted_scatter_df(
        scatter_data, parameters.marker_colortype
    )

    x: pd.Series = sorted_scatter_df[scatter_data.vector_col_names[0]]
    y: pd.Series = sorted_scatter_df[scatter_data.vector_col_names[1]]

    sizes: pd.Series = _determine_sizes(
        sorted_scatter_df,
        scatter_data.size_col_name,
        parameters.marker_default_size,
    )

    colors: pd.Series | None = _determine_colors(
        sorted_scatter_df,
        scatter_data,
        parameters,
        marker_maps.colormap,
        False,
    )

    border_colors: pd.Series | None = _determine_colors(
        sorted_scatter_df,
        scatter_data,
        parameters,
        marker_maps.border_colormap,
        True,
    )

    symbols: pd.Series | None = _determine_symbols(
        sorted_scatter_df,
        scatter_data.symbol_col_name,
        marker_maps.symbol_map,
    )

    hover_data: pd.DataFrame | None = _determine_hover_data(
        sorted_scatter_df,
        scatter_data.hover_data_col_names,
    )

    colorbar: dict[str, Any] | None = _determine_colorbar(
        parameters.marker_colorbar_title, parameters.marker_colortype
    )

    trace: dict[str, Any] = {
        "name": "",
        "x": x,
        "y": y,
        "mode": "markers",
        "marker": {
            "size": sizes,
            "color": colors,
            "colorscale": marker_maps.colorscale,
            "showscale": parameters.marker_colortype == "continuous",
            "colorbar": colorbar,
            "symbol": symbols,
            "opacity": parameters.marker_opacity,
            "sizeref": parameters.marker_sizeref,
            "sizemin": parameters.marker_sizemin,
            "sizemode": parameters.marker_sizemode,
            "line": {
                "color": border_colors,
                "width": 1,
            },
            "cmid": parameters.continuous_colorscale_midpoint,
        },
        "customdata": hover_data,
        "showlegend": False,
    }

    if scatter_data.dimensionality == 3:
        z: pd.Series = sorted_scatter_df[scatter_data.vector_col_names[2]]
        trace["z"] = z
        trace["type"] = "scatter3d"
    else:
        trace["type"] = "scattergl"

    hover_dict: dict[str, Any] = _get_hover_dict(
        scatter_data=scatter_data,
        parameters=parameters,
    )

    trace = trace | hover_dict

    return trace


def _generate_grouped_dummy_traces(
    scatter_data: ScatterData,
    marker_maps: MarkerMaps,
    parameters: PlotlyScatterParameters,
) -> list[dict[str, int]]:
    symbol_group_classes: list[str | None] = (
        scatter_data.symbol_column.unique().tolist()
        if scatter_data.symbol_column is not None
        else []
    )

    symbols: list[str | None] | list[int | None] = _generate_dummy_symbols(
        symbol_group_classes,
        marker_maps.symbol_map,
    )

    symbol_colors: list[str] = ["black"] * len(symbol_group_classes)

    color_group_classes: list[str | None] = (
        scatter_data.color_column.unique().tolist()
        if scatter_data.color_column is not None
        else []
    )

    color_colors: list[str | None] = _generate_dummy_colors(
        color_group_classes,
        symbol_group_classes,
        marker_maps.colormap,
        "discrete",
    )

    color_symbols: list[str] | list[int] = ["circle"] * len(
        color_group_classes
    )

    symbol_group_name: str = (
        scatter_data.symbol_col_name
        if scatter_data.symbol_col_name is not None
        else "Symbol"
    )

    symbol_dummy_traces: list[dict[str, Any]] = [
        {
            "name": symbol_group_class,
            "legendgroup": symbol_group_name,
            "legendgrouptitle": {"text": symbol_group_name},
            "x": [None],
            "y": [None],
            "showlegend": True,
            "mode": "markers",
            "marker": {
                "color": symbol_color,
                "symbol": symbol,
                "size": [10],
                "opacity": parameters.marker_opacity,
                "line": {
                    "color": "black",
                    "width": 1,
                },
            },
            "customdata": [symbol_group_class_full],
        }
        for symbol_group_class, symbol_group_class_full, symbol_color, symbol in zip(  # noqa: E501
            (
                _truncate(symbol_group_classes, parameters.legend_truncation)
                if parameters.legend_truncation is not None
                else symbol_group_classes
            ),  # noqa: E501
            symbol_group_classes,
            symbol_colors,
            symbols,
        )
    ]

    color_group_name: str = (
        scatter_data.color_col_name
        if scatter_data.color_col_name is not None
        else "Color"
    )

    color_dummy_traces: list[dict[str, Any]] = [
        {
            "name": color_group_class,
            "legendgroup": color_group_name,
            "legendgrouptitle": {"text": color_group_name},
            "x": [None],
            "y": [None],
            "showlegend": True,
            "mode": "markers",
            "marker": {
                "color": color_color,
                "symbol": color_symbol,
                "size": [10],
                "opacity": parameters.marker_opacity,
                "line": {
                    "color": color_color,
                    "width": 1,
                },
            },
            "customdata": [color_group_classes_full],
        }
        for color_group_class, color_group_classes_full, color_color, color_symbol in zip(  # noqa: E501
            (
                _truncate(color_group_classes, parameters.legend_truncation)
                if parameters.legend_truncation is not None
                else color_group_classes
            ),  # noqa: E501
            color_group_classes,
            color_colors,
            color_symbols,
        )
    ]

    dummy_traces: list[dict[str, Any]] = (
        symbol_dummy_traces + color_dummy_traces
    )

    for dummy_trace in dummy_traces:
        if scatter_data.dimensionality == 3:
            dummy_trace["type"] = "scatter3d"
            dummy_trace["z"] = [None]
        else:
            dummy_trace["type"] = "scattergl"

    return dummy_traces


def _generate_dummy_traces(
    scatter_data: ScatterData,
    marker_maps: MarkerMaps,
    parameters: PlotlyScatterParameters,
) -> list[dict[str, int]]:
    color_classes: list[str | None] = (
        scatter_data.color_column.unique().tolist()
        if scatter_data.color_column is not None
        and parameters.marker_colortype == "discrete"
        else [None]
    )

    symbol_classes: list[str | None] = (
        scatter_data.symbol_column.unique().tolist()
        if scatter_data.symbol_column is not None
        else [None]
    )

    product_classes: list[tuple[str | None, str | None]] = list(
        product(color_classes, symbol_classes)
    )

    colors: list[str | None] = _generate_dummy_colors(
        [pc[0] for pc in product_classes],
        symbol_classes,
        marker_maps.colormap,
        parameters.marker_colortype,
    )

    border_colors: list[str | None] = _generate_dummy_colors(
        [pc[0] for pc in product_classes],
        symbol_classes,
        marker_maps.border_colormap,
        parameters.marker_colortype,
    )

    symbols: list[str | None] | list[int | None] = _generate_dummy_symbols(
        [pc[1] for pc in product_classes],
        marker_maps.symbol_map,
    )

    names: list[str | None] = [
        _generate_dummy_trace_name(color_class, symbol_class)
        for color_class, symbol_class in product_classes
    ]

    dummy_traces: list[dict[str, Any]] = [
        {
            "name": name,
            "legendgroup": name,
            "x": [None],
            "y": [None],
            "showlegend": True,
            "mode": "markers",
            "marker": {
                "color": color,
                "symbol": symbol,
                "size": [10],
                "opacity": parameters.marker_opacity,
                "line": {
                    "color": border_color,
                    "width": 1,
                },
            },
        }
        for name, color, border_color, symbol in zip(
            (
                _truncate(names, parameters.legend_truncation)
                if parameters.legend_truncation is not None
                else names
            ),
            colors,
            border_colors,
            symbols,
        )
    ]

    for dummy_trace in dummy_traces:
        if scatter_data.dimensionality == 3:
            dummy_trace["type"] = "scatter3d"
            dummy_trace["z"] = [None]
        else:
            dummy_trace["type"] = "scattergl"

    return dummy_traces


def _generate_dummy_trace_name(
    color_class: str | None,
    symbol_class: str | None,
) -> str | None:
    match (color_class, symbol_class):
        case (None, None):
            return None
        case (None, symbol_class):
            return symbol_class
        case (color_class, None):
            return color_class
        case (color_class, symbol_class):
            return f"{color_class}, {symbol_class}"


def _generate_dummy_colors(
    color_classes: list[str | None],
    symbol_classes: list[str | None],
    colormap: dict[str, str] | None,
    colortype: Literal["discrete", "continuous"],
) -> list[str | None]:
    if colortype == "continuous":
        colors = ["black"] * len(symbol_classes)
    elif colormap is None:
        colors = [None] * len(color_classes)
    elif colortype == "discrete":
        colors: list[str | None] = [
            colormap[color_class] if color_class is not None else None
            for color_class in color_classes
        ]
    else:
        raise ValueError("Invalid color parameter combination.")

    return colors


def _truncate(names: list[str | None], threshold: int) -> list[str | None]:
    return [
        (
            n[: threshold + 1] + "..."
            if n is not None and len(n) > threshold
            else n
        )
        for n in names
    ]


def _generate_dummy_symbols(
    symbol_classes: list[str | None],
    symbol_map: dict[str, str] | dict[str, int] | None,
) -> list[str | None] | list[int | None]:
    if symbol_map is None or len(symbol_map) == 0:
        return cast(list[str | None], [None] * len(symbol_classes))

    symbols: list[str | None] | list[int | None] = [  # type: ignore
        (
            symbol_map[symbol_class]
            if symbol_class is not None
            else None
        )
        for symbol_class in symbol_classes
    ]

    return symbols


def _determine_sizes(
    sorted_scatter_df: pd.DataFrame,
    size_column_name: str | None,
    marker_default_size: int,
) -> pd.Series:
    sizes: pd.Series = (
        sorted_scatter_df[size_column_name]
        if size_column_name is not None
        else pd.Series([marker_default_size] * len(sorted_scatter_df))
    )

    return sizes


def _determine_colors(
    sorted_scatter_df: pd.DataFrame,
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
    colormap: dict[str, str] | None,
    border: bool,
) -> pd.Series | None:
    if scatter_data.color_col_name is None:
        colors: pd.Series | None = None
    elif parameters.marker_colortype == "discrete":
        if colormap is None:
            colors = None
        else:
            colors = sorted_scatter_df[scatter_data.color_col_name].apply(
                lambda cc: colormap[cc]
            )
    elif parameters.marker_colortype == "continuous":
        if border:
            colors = pd.Series("black", index=sorted_scatter_df.index)
        else:
            colors = sorted_scatter_df[scatter_data.color_col_name]
    else:
        raise ValueError("Invalid color parameter combination.")

    return colors


def _determine_symbols(
    sorted_scatter_df: pd.DataFrame,
    symbol_column_name: str | None,
    symbol_map: dict[str, str] | dict[str, int] | None,
) -> pd.Series | None:
    if (
        symbol_column_name is None
        or symbol_map is None
        or len(symbol_map) == 0
    ):
        return None

    symbols: pd.Series = sorted_scatter_df[symbol_column_name].apply(
        lambda sc: symbol_map[sc]  # type: ignore
    )

    return symbols


def _determine_hover_data(
    sorted_scatter_df: pd.DataFrame,
    hover_data_column_names: list[str] | None,
) -> pd.DataFrame | None:
    hover_data: pd.DataFrame | None = (
        sorted_scatter_df[hover_data_column_names]
        if hover_data_column_names is not None
        else None
    )

    return hover_data


def _determine_colorbar(
    marker_colorbar_title: str | None, marker_colortype
) -> dict[str, Any] | None:
    colorbar: dict[str, Any] | None = (
        {"title": {"text": marker_colorbar_title, "side": "top"}}
        if marker_colortype == "continuous"
        else None
    )

    return colorbar


def _generate_tracewise_layout(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
) -> dict[str, Any]:
    base_layout: dict[str, Any] = generate_layout(parameters)

    height: int | None = (
        parameters.graph_size[0] if parameters.graph_size is not None else None
    )

    width: int | None = (
        parameters.graph_size[1] if parameters.graph_size is not None else None
    )

    additional_layout: dict[str, Any] = {
        "height": height,
        "width": width,
    }

    if scatter_data.dimensionality == 2:
        axis_titles: dict[str, Any] = {
            "xaxis_title": scatter_data.vector_col_names[0],
            "yaxis_title": scatter_data.vector_col_names[1],
        }
    elif scatter_data.dimensionality == 3:
        axis_titles: dict[str, Any] = {
            "scene_xaxis_title": scatter_data.vector_col_names[0],
            "scene_yaxis_title": scatter_data.vector_col_names[1],
        }
        axis_titles["scene_zaxis_title"] = scatter_data.vector_col_names[2]
    else:
        raise ValueError(
            "Dimensionality of scatter data must be "
            f"2 or 3, but is {scatter_data.dimensionality}."
        )

    layout: dict[str, Any] = base_layout | additional_layout | axis_titles

    additional_legend: dict[str, Any] = {
        "tracegroupgap": 0,
        "itemclick": False,
        "itemdoubleclick": False,
    }

    layout["legend"] = layout["legend"] | additional_legend

    return layout


def _get_sorted_scatter_df(
    scatter_data: ScatterData,
    colortype: Literal["discrete", "continuous"],
) -> pd.DataFrame:
    if colortype == "discrete":
        if scatter_data.size_col_name is None:
            sorted_scatter_df: pd.DataFrame = scatter_data.dataframe
        else:
            sorted_scatter_df: pd.DataFrame = (
                scatter_data.dataframe.sort_values(
                    by=[scatter_data.size_col_name],
                    ascending=False,
                )
            )
    elif colortype == "continuous":
        if scatter_data.color_col_name is None:
            sorted_scatter_df: pd.DataFrame = scatter_data.dataframe
        else:
            sorted_scatter_df: pd.DataFrame = (
                scatter_data.dataframe.sort_values(
                    by=[scatter_data.color_col_name],
                    ascending=True,
                    key=abs,
                )
            )
    else:
        raise ValueError("Invalid color parameter combination.")

    return sorted_scatter_df


def _get_hover_dict(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
) -> dict[str, Any]:
    if parameters.disable_hover:
        hover_dict: dict[str, Any] = {
            "hoverinfo": "skip",
            "hovertemplate": " <extra></extra>",
        }
    else:
        if scatter_data.hover_data_col_names is None:
            hover_dict: dict[str, Any] = {}
        else:
            hover_dict: dict[str, Any] = {
                "hovertemplate": (
                    "<br>".join(
                        [
                            f"<b>{column_name}</b>: %{{customdata[{i}]}}"
                            for i, column_name in enumerate(
                                scatter_data.hover_data_col_names
                            )
                        ]
                    )
                )
            }

    return hover_dict
