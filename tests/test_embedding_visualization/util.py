"""Module concerning test utilities."""

import logging

from dataclasses import dataclass, field

from plotly.graph_objects import Figure

from embedding_visualization.marker_maps import MarkerMaps
from embedding_visualization.parameters import PlotlyScatterParameters
from embedding_visualization.scatter_data import ScatterData
from embedding_visualization.single_trace_scatter_generation import (
    generate_single_trace_plotly_scatter,
)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Case:
    name: str

    scatter_data: ScatterData
    parameters: PlotlyScatterParameters
    marker_maps: MarkerMaps

    x_ref: list[float]
    y_ref: list[float]
    z_ref: list[float]

    colors_ref: list[str]
    symbols_ref: list[str] | list[int]
    legend_names_ref: list[str]
    hoverdata_ref: list[list]

    num_legend_groups: int = field(init=False)

    figure: Figure = field(init=False)
    figure_dict: dict = field(init=False)

    def __post_init__(self) -> None:
        self._set_num_legend_groups()
        self._set_figure()

    def _set_num_legend_groups(self) -> None:
        object.__setattr__(
            self, "num_legend_groups", len(self.legend_names_ref)
        )

    def _set_figure(self) -> None:
        figure: Figure = generate_single_trace_plotly_scatter(
            scatter_data=self.scatter_data,
            parameters=self.parameters,
            marker_maps=self.marker_maps,
        )
        object.__setattr__(self, "figure", figure)
        object.__setattr__(self, "figure_dict", figure.to_dict())
