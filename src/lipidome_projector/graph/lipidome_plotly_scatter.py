"""Module concerning the generation of lipidome plotly scatter plots."""

import logging

from dataclasses import dataclass
from base64 import b64encode
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from plotly.graph_objects import Figure

from embedding_visualization.parameters import PlotlyScatterParameters
from embedding_visualization.scatter_data import ScatterData
from embedding_visualization.scatter_generation import generate_plotly_scatter

from lipid_vector_space.embedding.scaling import (
    linear_scaling,
    min_max_series,
)

from lipidome_projector.graph.lipid_plotly_markers import (
    CATEGORY_SYMBOLS_2D,
    CATEGORY_SYMBOLS_3D,
)


logger: logging.Logger = logging.getLogger(__name__)


_SCALED_ABUNDANCE_COL_NAME: str = "SCALED_ABUNDANCE"


# TODO: Check, whether a base-class shared with DB parameters makes sense.
@dataclass(frozen=True)
class LipidomeScatterParameters:
    df: pd.DataFrame

    lipid_col_name: str
    category_col_name: str
    class_col_name: str
    vector_col_names_2d: tuple[str, str]
    vector_col_names_3d: tuple[str, str, str]

    lipidome_filter: pd.Index | None = None
    lipid_filter: pd.Index | None = None

    scaling_method: str | None = None
    scaling_params: dict[str, Any] | None = None

    dimensionality: int = 2

    marker_symbols: bool = True
    marker_opacity: float = 1.0
    marker_sizemin: float | None = None
    marker_sizemode: Literal["area", "diameter"] = "area"

    colortype: Literal["lipidome", "change"] = "lipidome"

    abundance_col_name: str | None = None
    lipidome_col_name: str | None = None

    change_col_name: str | None = None
    colorscale_name: str | None = None
    colorscale_midpoint: float | None = None
    colorbar_title: str | None = None

    lipidome_colormap: dict[str, str] | None = None

    disable_hover: bool = False

    legend_position: Literal["top", "bottom", "left", "right"] = "top"
    legend_type: Literal["normal", "grouped"] = "normal"
    legend_truncation: int | None = None

    graph_size: tuple[int, int] = (1000, 1000)
    title: str | None = None

    def __post_init__(self) -> None:
        self._check_dimensionality()
        self._check_colortype()

    def _check_dimensionality(self) -> None:
        if self.dimensionality not in [2, 3]:
            raise ValueError(
                f"Invalid dimensionality '{self.dimensionality}'. "
                "Must be either 2 or 3."
            )

    def _check_colortype(self) -> None:
        if self.colortype not in ["lipidome", "change"]:
            raise ValueError(
                f"Invalid color type '{self.colortype}'. "
                "Must be either 'lipidome' or 'change'."
            )

        if self.colortype == "change":
            if self.lipidome_colormap is not None:
                raise ValueError(
                    "Cannot use 'change' color type with a custom colormap."
                )

            if self.change_col_name is None:
                raise ValueError(
                    "Cannot use 'change' color type without a change column."
                )

        if self.colortype == "lipidome":
            if self.abundance_col_name is None:
                raise ValueError(
                    "Cannot use 'lipidome' color type without an abundance "
                    "column."
                )
            if self.lipidome_col_name is None:
                raise ValueError(
                    "Cannot use 'lipidome' color type without a lipidome "
                    "column."
                )
            if self.colorscale_name is not None:
                raise ValueError(
                    "Cannot use colorscale with 'lipidome' color type."
                )
            if self.colorscale_midpoint is not None:
                raise ValueError(
                    "Cannot use colorscale midpoint with 'lipidome' "
                    "color type."
                )


def gen_empty_plot() -> Figure:
    """Generate an empty plot.
    :returns: The generated empty plot.
    """
    empty_figure: Figure = Figure()
    empty_figure.update_layout(
        modebar=dict(
            remove=[
                "toimage",
                "pan",
                "zoom",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "resetScale2d",
            ]
        )
    )
    empty_figure.update_xaxes(
        showgrid=False, zeroline=False, showticklabels=False
    )
    empty_figure.update_yaxes(
        showgrid=False, zeroline=False, showticklabels=False
    )
    return empty_figure


# TODO: Abstact into class (move empty plot in there too).
# Check if shared base class with DB makes sense.
def gen_lipidome_scatter(params: LipidomeScatterParameters) -> Figure:
    """Generate a lipidome scatter plot.
    :param params: Parameters for the scatter plot.
    :returns: The generated scatter plot.
    """
    scatter_data: ScatterData = _gen_scatter_data(params)

    plotly_scatter_parameters: PlotlyScatterParameters = (
        _gen_plotly_scatter_parameters(params, scatter_data.dimensionality)
    )

    figure: Figure = generate_plotly_scatter(
        scatter_data,
        plotly_scatter_parameters,
    )

    return figure


def _gen_plotly_scatter_parameters(
    params: LipidomeScatterParameters,
    dimensionality: Literal[2, 3],
) -> PlotlyScatterParameters:
    marker_symbol_map: dict[str, str] | dict[str, int] | None = (
        _det_marker_symbol_map(
            params.marker_symbols,
            dimensionality,
        )
    )

    marker_colortype = _det_marker_colortype(params.colortype)

    plotly_params: PlotlyScatterParameters = PlotlyScatterParameters(
        explicit_marker_stacking=True,
        marker_symbol_map=marker_symbol_map,
        marker_colormap=params.lipidome_colormap,
        marker_colortype=marker_colortype,
        marker_colorbar_title=params.colorbar_title,
        continuous_colorscale_name=params.colorscale_name,
        continuous_colorscale_midpoint=params.colorscale_midpoint,
        marker_default_size=5,
        marker_sizemin=params.marker_sizemin,
        marker_sizemode=params.marker_sizemode,
        marker_opacity=params.marker_opacity,
        disable_hover=params.disable_hover,
        graph_size=params.graph_size,
        legend_position=params.legend_position,
        legend_type=params.legend_type,
        legend_truncation=params.legend_truncation,
        title=params.title,
    )

    return plotly_params


def _det_marker_symbol_map(
    marker_symbols: bool,
    dimensionality: int,
) -> dict[str, str] | dict[str, int] | None:
    marker_symbol_map: dict[str, str] | dict[str, int] | None = (
        (CATEGORY_SYMBOLS_2D if dimensionality == 2 else CATEGORY_SYMBOLS_3D)
        if marker_symbols
        else None
    )

    return marker_symbol_map


def _det_marker_colortype(
    colortype: Literal["lipidome", "change"],
) -> Literal["discrete", "continuous"]:
    marker_colortype: Literal["discrete", "continuous"] = (
        "discrete" if colortype == "lipidome" else "continuous"
    )

    return marker_colortype


def _gen_scatter_data(params: LipidomeScatterParameters) -> ScatterData:
    symbol_col_name: str | None = (
        params.category_col_name if params.marker_symbols else None
    )

    vector_col_names: tuple[str, ...] = (
        params.vector_col_names_2d
        if params.dimensionality == 2
        else params.vector_col_names_3d
    )

    if params.colortype == "lipidome":
        scatter_data: ScatterData = _gen_lipidomes_scatter_data(
            df=params.df,
            lipidome_col_name=params.lipidome_col_name,  # type: ignore
            lipid_col_name=params.lipid_col_name,
            category_col_name=params.category_col_name,
            abundance_col_name=params.abundance_col_name,  # type: ignore
            scaled_abundance_col_name=_SCALED_ABUNDANCE_COL_NAME,
            vector_col_names=vector_col_names,
            symbol_col_name=symbol_col_name,
            lipidome_filter=params.lipidome_filter,
            lipid_filter=params.lipid_filter,
            scaling_method=params.scaling_method,
            scaling_params=params.scaling_params,
        )
    elif params.colortype == "change":
        scatter_data = _gen_change_scatter_data(
            df=params.df,
            change_col_name=params.change_col_name,  # type: ignore
            lipid_col_name=params.lipid_col_name,
            category_col_name=params.category_col_name,
            vector_col_names=vector_col_names,
            symbol_col_name=symbol_col_name,
            lipid_filter=params.lipid_filter,
        )
    else:
        raise ValueError(
            f"Invalid color type '{params.colortype}'. "
            "Must be either 'lipidome' or 'change'."
        )

    return scatter_data


def _gen_lipidomes_scatter_data(
    df: pd.DataFrame,
    lipidome_col_name: str,
    lipid_col_name: str,
    category_col_name: str,
    abundance_col_name: str,
    scaled_abundance_col_name: str,
    vector_col_names: tuple[str, ...],
    symbol_col_name: str | None,
    lipidome_filter: pd.Index | None = None,
    lipid_filter: pd.Index | None = None,
    scaling_method: str | None = None,
    scaling_params: dict[str, Any] | None = None,
) -> ScatterData:
    # TODO: Remove side-effects.
    # Construct new df with only relevant columns.
    _add_scaled_abundances(
        df=df,
        abundance_col_name=abundance_col_name,
        scaled_abundance_col_name=scaled_abundance_col_name,
        scaling_method=scaling_method,
        scaling_params=scaling_params,
    )

    if lipidome_filter is not None:
        df = _apply_col_filter(
            df=df,
            col_name=lipidome_col_name,
            filter_index=lipidome_filter,
        )

    if lipid_filter is not None:
        df = _apply_col_filter(
            df=df,
            col_name=lipid_col_name,
            filter_index=lipid_filter,
        )

    df = df.dropna(subset=[abundance_col_name])

    scatter_data: ScatterData = ScatterData(
        dataframe=df,
        vector_col_names=list(vector_col_names),
        color_col_name=lipidome_col_name,
        symbol_col_name=symbol_col_name,
        size_col_name=scaled_abundance_col_name,
        hover_data_col_names=[
            lipidome_col_name,
            lipid_col_name,
            category_col_name,
            abundance_col_name,
        ],
    )

    return scatter_data


def _add_scaled_abundances(
    df: pd.DataFrame,
    abundance_col_name: str,
    scaled_abundance_col_name: str,
    scaling_method: str | None = None,
    scaling_params: dict[str, Any] | None = None,
) -> None:
    if scaling_method is not None:
        if scaling_params is None:
            raise ValueError(
                "Must provide scaling parameters when using scaling method."
            )
        df[scaled_abundance_col_name] = _apply_scaling(
            df[abundance_col_name],
            scaling_method,
            scaling_params,
        )
    else:
        df[scaled_abundance_col_name] = df[abundance_col_name]


def _apply_col_filter(
    df: pd.DataFrame,
    col_name: str,
    filter_index: pd.Index,
) -> pd.DataFrame:
    index_intersection: pd.Index = filter_index.intersection(
        pd.Index(df[col_name])
    ).rename(col_name)

    return df.set_index(col_name).loc[index_intersection].reset_index()


def _gen_change_scatter_data(
    df: pd.DataFrame,
    change_col_name: str,
    lipid_col_name: str,
    category_col_name: str,
    vector_col_names: tuple[str, ...],
    symbol_col_name: str | None,
    lipid_filter: pd.Index | None = None,
) -> ScatterData:
    if lipid_filter is not None:
        df = _apply_col_filter(
            df=df,
            col_name=lipid_col_name,
            filter_index=lipid_filter,
        )

    scatter_data: ScatterData = ScatterData(
        dataframe=df,
        vector_col_names=list(vector_col_names),
        color_col_name=change_col_name,
        symbol_col_name=symbol_col_name,
        hover_data_col_names=[
            change_col_name,
            lipid_col_name,
            category_col_name,
        ],
    )

    return scatter_data


def _apply_scaling(
    series: pd.Series, scaling_method: str, scaling_params: dict[str, Any]
) -> pd.Series:
    if scaling_method == "linear":
        scaled_series: pd.Series = linear_scaling(series, **scaling_params)
    elif scaling_method == "min_max":
        scaled_series = min_max_series(series, **scaling_params)
    else:
        raise ValueError(f"Invalid scaling method '{scaling_method}'.")

    return scaled_series
