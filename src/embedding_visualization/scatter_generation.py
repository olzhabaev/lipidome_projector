"""Module concerning plotly scatter plots."""

import logging

from pandas.api.types import is_numeric_dtype
from plotly.graph_objects import Figure

from embedding_visualization.marker_maps import (
    MarkerMaps,
)
from embedding_visualization.parameters import (
    PlotlyScatterParameters,
)
from embedding_visualization.px_scatter_generation import generate_px_scatter
from embedding_visualization.scatter_data import ScatterData
from embedding_visualization.single_trace_scatter_generation import (
    generate_single_trace_plotly_scatter,
)


logger: logging.Logger = logging.getLogger(__name__)


def generate_plotly_scatter(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
) -> Figure:
    """Generate a plotly scatter plot.
    :param scatter_data: Scatter data.
    :param parameters: Plotly parameters.
    :returns: Plotly scatter plot figure.
    """
    _check_prameter_data_consistency(scatter_data, parameters)

    marker_maps: MarkerMaps = MarkerMaps.from_parameters(
        parameters.marker_colortype,
        parameters.marker_colormap,
        parameters.marker_symbol_map,
        parameters.continuous_colorscale_name,
        scatter_data.color_column,
        scatter_data.symbol_column,
        scatter_data.filtered_name,
        scatter_data.dimensionality,
    )

    figure: Figure = (
        generate_single_trace_plotly_scatter(
            scatter_data, parameters, marker_maps
        )
        if parameters.explicit_marker_stacking
        else generate_px_scatter(scatter_data, parameters, marker_maps)
    )

    return figure


def _check_prameter_data_consistency(
    scatter_data: ScatterData,
    parameters: PlotlyScatterParameters,
) -> None:
    if parameters.marker_colortype == "continuous":
        if scatter_data.color_column is None:
            raise ValueError(
                "Continuous marker color requires a color column in the data."
            )

        if not is_numeric_dtype(scatter_data.color_column):
            raise ValueError(
                "Continuous marker color requires a numeric color column."
            )
