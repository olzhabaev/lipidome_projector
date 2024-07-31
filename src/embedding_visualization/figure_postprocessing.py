"""Module concerning the postprocessing of plotly scatter figures."""


import logging

from typing import Literal

from plotly.graph_objects import Figure


logger: logging.Logger = logging.getLogger(__name__)


def postprocess_figure(
    figure: Figure,
    hover_data_column_names: list[str] | None,
    border_colormap: dict[str, str] | None,
    marker_sizeref: float | None,
    marker_sizemode: Literal["diameter", "area"] | None,
    disable_hover: bool,
    dimensionality: Literal[2, 3],
) -> None:
    """Postprocess plotly scatter figure. The input figure is modified.
    :param figure: Plotly scatter figure.
    :param hover_data_column_names: Hover data column names.
    :param border_colormap: Marker border colormap.
    :param marker_sizeref: Marker size reference.
    :param marker_sizemode: Marker size mode.
    :param disable_hover: Whether to disable hover.
    :param dimensionality: Dimensionality of the scatter plot.
    """
    figure.update_yaxes(scaleanchor="x", scaleratio=1)

    if border_colormap is not None:
        _set_figure_border_color(figure, border_colormap)

    if hover_data_column_names is not None:
        _set_hover_data(
            figure,
            hover_data_column_names,
        )

    if disable_hover:
        _disable_hover(figure)

    if marker_sizeref is not None:
        _set_marker_sizeref(figure, marker_sizeref)

    if marker_sizemode is not None:
        _set_marker_sizemode(figure, marker_sizemode)

    _disable_legend_title(figure)

    _set_uirevision(figure, dimensionality)


def _set_marker_sizeref(figure: Figure, marker_sizeref: float) -> None:
    figure.update_traces({"marker": {"sizeref": marker_sizeref}})


def _set_marker_sizemode(
    figure: Figure, marker_sizemode: Literal["diameter", "area"]
) -> None:
    figure.update_traces(marker_sizemode=marker_sizemode)


def _set_uirevision(figure: Figure, dimensionality: Literal[2, 3]) -> None:
    figure["layout"]["uirevision"] = f"{dimensionality}D"  # type: ignore


def _set_hover_data(
    figure: Figure,
    hover_data_column_names: list[str],
) -> None:
    figure.update_traces(
        hovertemplate=(
            "<br>".join(
                [
                    f"<b>{column_name}</b>: %{{customdata[{i}]}}"
                    for i, column_name in enumerate(hover_data_column_names)
                ]
            )
        )
    )


def _disable_hover(figure: Figure) -> None:
    figure.update_traces(hoverinfo="skip", hovertemplate=" <extra></extra>")


def _set_figure_border_color(figure: Figure, colormap: dict[str, str]) -> None:
    for color_class, color in colormap.items():
        figure.update_traces(
            marker={
                "line": {
                    "width": 1,
                    "color": color,
                }
            },
            selector=(lambda trace: (trace.name.startswith(color_class))),
        )


def _disable_legend_title(figure: Figure) -> None:
    figure.update_layout(legend_title="")
