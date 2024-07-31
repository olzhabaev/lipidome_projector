"""Module concerning the generation of marker maps for plotly
scatter plots."""

import logging

from dataclasses import dataclass
from typing import Literal, Self

import pandas as pd

from embedding_visualization.colors import (
    CONTINUOUS_COLORSCALES,
    darken_hex_color,
    generate_discrete_hex_colormap,
)
from embedding_visualization.symbols import gen_symbol_map


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MarkerMaps:
    colormap: dict[str, str] | None
    border_colormap: dict[str, str] | None
    symbol_map: dict[str, str] | dict[str, int] | None
    colorscale: list[str] | None = None

    @classmethod
    def from_parameters(
        cls,
        marker_colotype: Literal["discrete", "continuous"],
        marker_colormap: dict[str, str] | None,
        marker_symbol_map: dict[str, str] | dict[str, int] | None,
        colorscale_name: str | None,
        color_column: pd.Series | None,
        symbol_column: pd.Series | None,
        filtered_name: str | None,
        dimensionality: Literal[2, 3],
    ) -> Self:
        """Generate marker color and symbol maps.
        :param parameters: Plotly scatter parameters.
        :param scatter_data: Scatter data.
        :return: Marker color and symbol maps.
        """
        colormap: dict[str, str] | None = (
            cls._get_marker_colormap(
                marker_colormap,
                color_column,
                filtered_name,
            )
            if marker_colotype == "discrete"
            else None
        )

        border_colormap: dict[str, str] | None = (
            cls._get_marker_border_colormap(colormap)
            if colormap is not None
            else None
        )

        symbol_map: dict = cls._get_symbol_map(
            marker_symbol_map,
            symbol_column,
            filtered_name,
            dimensionality,
        )

        colorscale: list[str] | None = cls._get_colorscale(
            colorscale_name,
        )

        marker_maps: Self = cls(
            colormap=colormap,
            border_colormap=border_colormap,
            symbol_map=symbol_map,
            colorscale=colorscale,
        )

        return marker_maps

    @staticmethod
    def _get_symbol_map(
        additional_symbol_map: dict | None,
        symbol_column: pd.Series | None,
        filtered_name: str | None,
        dimensionality: Literal[2, 3],
    ) -> dict[str, str] | dict[str, int]:
        if symbol_column is None:
            symbol_map: dict = {}
        else:
            symbol_map: dict = gen_symbol_map(
                symbol_column.unique().tolist(), dimensionality
            )
        if additional_symbol_map is not None:
            symbol_map |= additional_symbol_map

        if filtered_name is not None:
            # TODO Add handling of default filtered shape.
            symbol_map[filtered_name] = (  # type: ignore
                0 if dimensionality == 2 else "circle"
            )

        return symbol_map

    @staticmethod
    def _get_marker_colormap(
        additional_colormap: dict[str, str] | None,
        color_column: pd.Series | None,
        filtered_name: str | None,
    ) -> dict[str, str]:
        if color_column is not None:
            colormap: dict[str, str] = generate_discrete_hex_colormap(
                color_column.unique().tolist(),
                "T10",
            )
        else:
            colormap: dict[str, str] = {}

        if additional_colormap is not None:
            colormap |= additional_colormap

        if filtered_name is not None:
            # TODO Add handling of default filtered color.
            colormap[filtered_name] = "#D3D3D3"

        return colormap

    @staticmethod
    def _get_marker_border_colormap(
        colormap: dict[str, str] | None,
    ) -> dict[str, str]:
        if colormap is not None:
            border_colormap: dict[str, str] = {
                color_class: darken_hex_color(color)
                for color_class, color in colormap.items()
            }
        else:
            border_colormap = {}

        return border_colormap

    @staticmethod
    def _get_colorscale(colorscale_name: str | None) -> list[str] | None:
        colorscale: list[str] | None = (
            CONTINUOUS_COLORSCALES[colorscale_name]
            if colorscale_name is not None
            else None
        )

        return colorscale
