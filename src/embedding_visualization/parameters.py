"""Module concerning plotly scatter parameters."""


import logging

from dataclasses import dataclass
from typing import Literal


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PlotlyScatterParameters:
    explicit_marker_stacking: bool = False

    marker_sizemode: Literal["area", "diameter"] = "area"
    marker_default_size: int = 5
    marker_sizemin: float | None = None
    marker_sizemax: float | None = None
    marker_sizeref: float | None = None

    marker_opacity: float = 1.0

    marker_colortype: Literal["discrete", "continuous"] = "discrete"

    marker_colormap: dict[str, str] | None = None

    continuous_colorscale_name: str | None = None
    continuous_colorscale_midpoint: float | None = None
    marker_colorbar_title: str | None = None

    marker_symbol_map: dict[str, str] | dict[str, int] | None = None

    layout_font_size: int = 15
    legend_font_size: int = 15
    legend_position: Literal["top", "bottom", "left", "right"] = "top"
    legend_type: Literal["normal", "grouped"] = "normal"
    legend_truncation: int | None = None

    disable_hover: bool = False

    graph_size: tuple[int, int] = (1000, 1000)

    title: str | None = None

    def __post_init__(self) -> None:
        self._check_marker_parameters()

    def _check_marker_parameters(self) -> None:
        if self.marker_colortype == "continuous":
            if self.marker_colormap is not None:
                raise ValueError(
                    "Marker colormap cannot be set "
                    "for continuous marker color."
                )
        elif self.marker_colortype == "discrete":
            if self.continuous_colorscale_name is not None:
                raise ValueError(
                    "Continuous colorscale cannot be set "
                    "for discrete marker color."
                )
            if self.continuous_colorscale_midpoint is not None:
                raise ValueError(
                    "Continuous colorscale midpoint cannot be set "
                    "for discrete marker color."
                )
            if self.marker_colorbar_title is not None:
                raise ValueError(
                    "Marker colorbar title cannot be set "
                    "for discrete marker color."
                )
        else:
            raise ValueError(
                f"Invalid marker color type: {self.marker_colortype}"
            )
