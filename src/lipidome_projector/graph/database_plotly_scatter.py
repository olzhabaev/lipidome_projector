"""Module concerning the generation of database plotly scatter plots."""

import logging

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

from pandas.api.types import is_numeric_dtype
from plotly.graph_objects import Figure

from embedding_visualization.scatter_data import ScatterData
from embedding_visualization.scatter_generation import generate_plotly_scatter
from embedding_visualization.parameters import PlotlyScatterParameters

from lipidome_projector.graph.lipid_plotly_markers import (
    CATEGORY_COLORS,
    CATEGORY_SYMBOLS_2D,
    CATEGORY_SYMBOLS_3D,
)


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DBScatterParameters:
    vectors_df: pd.DataFrame
    database_df: pd.DataFrame

    name_column_name: str
    category_column_name: str
    class_column_name: str
    mass_column_name: str
    id_column_name: str

    colors: Literal["category", "class", "mass", "other", "none"]
    symbols: Literal["category", "class", "none"]

    hover_data: list[Literal["id", "name", "category", "class", "mass"]]

    opacity: float

    graph_size: tuple[int, int]

    other_color_column_name: str | None = None
    index_filter: pd.Index | None = None
    additional_color_map: dict[str, str] | None = None
    additional_symbol_map: dict[str, str] | dict[str, int] | None = None

    vector_column_names: list[str] = field(init=False)
    color_column_name: str | None = field(init=False)
    symbol_column_name: str | None = field(init=False)
    hover_data_column_names: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self._validate_database_df()
        self._validate_vectors_df()
        self._validate_marker_parameters()
        self._validate_graph_size()
        self._set_color_column_name()
        self._set_symbol_column_name()
        self._set_hover_data_column_names()
        self._set_vector_column_names()

    def _validate_database_df(self) -> None:
        if self.name_column_name not in self.database_df.columns:
            raise ValueError(f"'{self.name_column_name}' column missing.")

        if self.category_column_name not in self.database_df.columns:
            raise ValueError(f"'{self.category_column_name}' column missing.")

        if self.class_column_name not in self.database_df.columns:
            raise ValueError(f"'{self.class_column_name}' column missing.")

        if self.mass_column_name not in self.database_df.columns:
            raise ValueError(f"'{self.mass_column_name}' column missing.")

        duplicated_columns: list[str] = self.database_df.columns[
            self.database_df.columns.duplicated()
        ].to_list()

        if duplicated_columns:
            raise ValueError(
                "Database dataframe has duplicated columns: "
                f"{duplicated_columns}"
            )

    def _validate_vectors_df(self) -> None:
        if not 2 <= len(self.vectors_df.columns) <= 3:
            raise ValueError(
                "Vectors dataframe must have 2 or 3 columns, "
                f"but has {len(self.vectors_df.columns)}"
            )

        if self.vectors_df.isna().any().any():
            raise ValueError("Vectors dataframe contains NaN values.")

    def _validate_marker_parameters(self) -> None:
        if self.symbols not in ["category", "class", "none"]:
            raise ValueError(
                f"Invalid marker parameter '{self.symbols}'. "
                "Must be either 'category', 'class' or 'none'."
            )

        if self.colors not in ["category", "class", "mass", "other", "none"]:
            raise ValueError(
                f"Invalid color parameter '{self.colors}'. "
                "Must be either 'category', 'class' or 'none'."
            )

        if not set(self.hover_data).issubset(
            ["id", "name", "category", "class", "mass"]
        ):
            raise ValueError(
                f"Invalid hover_data parameter '{self.hover_data}'. "
                "Must be a list of either 'id', 'name', "
                "'category', 'class' or 'mass'."
            )

    def _validate_graph_size(self) -> None:
        if len(self.graph_size) != 2:
            raise ValueError(
                f"Invalid graph size parameter '{self.graph_size}'. "
                "Must be a tuple of two integers."
            )

        if not all(isinstance(element, int) for element in self.graph_size):
            raise ValueError(
                f"Invalid graph size parameter '{self.graph_size}'. "
                "Must be a tuple of two integers."
            )

    def _set_color_column_name(self) -> None:
        if self.colors == "category":
            object.__setattr__(
                self, "color_column_name", self.category_column_name
            )
        elif self.colors == "class":
            object.__setattr__(
                self, "color_column_name", self.class_column_name
            )
        elif self.colors == "none":
            object.__setattr__(self, "color_column_name", None)
        elif self.colors == "mass":
            object.__setattr__(
                self, "color_column_name", self.mass_column_name
            )
        elif self.colors == "other":
            object.__setattr__(
                self,
                "color_column_name",
                self.other_color_column_name,
            )
        else:
            raise ValueError(
                f"Invalid color parameter '{self.colors}'. "
                "Must be either 'category' or 'class'."
            )

    def _set_symbol_column_name(self) -> None:
        if self.symbols == "category":
            object.__setattr__(
                self, "symbol_column_name", self.category_column_name
            )
        elif self.symbols == "class":
            object.__setattr__(
                self, "symbol_column_name", self.class_column_name
            )
        elif self.symbols == "none":
            object.__setattr__(self, "symbol_column_name", None)
        else:
            raise ValueError(
                f"Invalid marker parameter '{self.symbols}'. "
                "Must be either 'category' or 'class'."
            )

    def _set_hover_data_column_names(self) -> None:
        hover_data_column_names: list[str] = []
        for hover_data_element in self.hover_data:
            if hover_data_element == "id":
                hover_data_column_names.append(self.id_column_name)
            elif hover_data_element == "name":
                hover_data_column_names.append(self.name_column_name)
            elif hover_data_element == "category":
                hover_data_column_names.append(self.category_column_name)
            elif hover_data_element == "class":
                hover_data_column_names.append(self.class_column_name)
            elif hover_data_element == "mass":
                hover_data_column_names.append(self.mass_column_name)
            else:
                raise ValueError(
                    f"Invalid hover_data parameter '{hover_data_element}'. "
                    "Must be either 'id', 'name', 'category', 'class' "
                    "or 'mass'."
                )

        object.__setattr__(
            self, "hover_data_column_names", hover_data_column_names
        )

    def _set_vector_column_names(self) -> None:
        object.__setattr__(
            self,
            "vector_column_names",
            self.vectors_df.columns.to_list(),
        )


# TODO: Abstract into class.
def generate_database_scatter(
    scatter_parameters: DBScatterParameters,
) -> Figure:
    plot_df: pd.DataFrame = _generate_plot_df(scatter_parameters)

    scatter_data: ScatterData = _generate_scatter_data(
        scatter_parameters, plot_df
    )

    plotly_scatter_parameters: PlotlyScatterParameters = (
        _generate_plotly_scatter_parameters(
            scatter_parameters, scatter_data.dimensionality
        )
    )

    figure: Figure = generate_plotly_scatter(
        scatter_data, plotly_scatter_parameters
    )

    return figure


def _generate_plot_df(
    scatter_parameters: DBScatterParameters,
) -> pd.DataFrame:
    new_column_names: list[str] = list(
        scatter_parameters.vector_column_names
        if len(scatter_parameters.vectors_df.columns) == 3
        else scatter_parameters.vector_column_names[:2]
    )

    plot_df: pd.DataFrame = (
        pd.concat(
            [
                scatter_parameters.database_df,
                scatter_parameters.vectors_df.set_axis(
                    new_column_names, axis="columns"
                ),
            ],
            axis="columns",
            join="inner",
        )
        .rename_axis(scatter_parameters.id_column_name)
        .fillna(
            {
                scatter_parameters.name_column_name: "UNDEFINED",
                scatter_parameters.category_column_name: "UNDEFINED",
                scatter_parameters.class_column_name: "UNDEFINED",
                scatter_parameters.mass_column_name: (
                    scatter_parameters.database_df[
                        scatter_parameters.mass_column_name
                    ].mean()
                ),
            }
        )
    )

    return plot_df


def _generate_scatter_data(
    scatter_parameters: DBScatterParameters,
    plot_df: pd.DataFrame,
) -> ScatterData:
    color_column_name: str | None = scatter_parameters.color_column_name
    symbol_column_name: str | None = scatter_parameters.symbol_column_name

    scatter_data: ScatterData = ScatterData(
        dataframe=plot_df,
        vector_col_names=scatter_parameters.vector_column_names,
        color_col_name=color_column_name,
        symbol_col_name=symbol_column_name,
        size_col_name=scatter_parameters.mass_column_name,
        hover_data_col_names=scatter_parameters.hover_data_column_names,
        index_filter=scatter_parameters.index_filter,
    )

    return scatter_data


def _generate_plotly_scatter_parameters(
    db_scatter_parameters: DBScatterParameters,
    dimensionality: Literal[2, 3],
) -> PlotlyScatterParameters:
    symbol_map: dict[str, str] | dict[str, int] = _get_symbol_map(
        db_scatter_parameters,
        dimensionality,
    )

    marker_colortype: Literal["discrete", "continuous"] = (
        _get_marker_colortype(db_scatter_parameters)
    )

    colormap: dict[str, str] | None = (
        _get_colormap(db_scatter_parameters)
        if marker_colortype == "discrete"
        else None
    )

    # TODO Parameterize.
    colorscale: str | None = (
        "thermal" if marker_colortype == "continuous" else None
    )

    plotly_scatter_parameters: PlotlyScatterParameters = (
        PlotlyScatterParameters(
            explicit_marker_stacking=False,
            graph_size=db_scatter_parameters.graph_size,
            marker_colormap=colormap,
            marker_colortype=marker_colortype,
            continuous_colorscale_name=colorscale,
            marker_symbol_map=symbol_map,
            marker_sizemax=10,
            marker_opacity=db_scatter_parameters.opacity,
        )
    )

    return plotly_scatter_parameters


def _get_marker_colortype(
    db_scatter_parameters: DBScatterParameters,
) -> Literal["discrete", "continuous"]:
    if db_scatter_parameters.colors in ["category", "class", "none"]:
        marker_color_type: Literal["discrete", "continuous"] = "discrete"
    elif db_scatter_parameters.colors in ["mass"]:
        marker_color_type = "continuous"
    elif db_scatter_parameters.colors in ["other"]:
        if db_scatter_parameters.other_color_column_name is None:
            raise ValueError(
                "Color type 'other' requires a column name "
                "for the color values."
            )
        if db_scatter_parameters.other_color_column_name not in (
            db_scatter_parameters.database_df.columns
        ):
            raise ValueError(
                f"Column '{db_scatter_parameters.other_color_column_name}' "
                "not found in database dataframe."
            )
        if is_numeric_dtype(
            db_scatter_parameters.database_df[
                db_scatter_parameters.other_color_column_name
            ]
        ):
            marker_color_type = "continuous"
        else:
            marker_color_type = "discrete"
    else:
        raise ValueError(
            f"Invalid color type '{db_scatter_parameters.colors}'"
        )

    return marker_color_type


def _get_colormap(
    db_scatter_parameters: DBScatterParameters,
) -> dict[str, str]:
    colormap: dict[str, str] = CATEGORY_COLORS

    if db_scatter_parameters.additional_color_map is not None:
        colormap.update(db_scatter_parameters.additional_color_map)

    return colormap


def _get_symbol_map(
    db_scatter_parameters: DBScatterParameters,
    dimensionality: Literal[2, 3],
) -> dict[str, str] | dict[str, int]:
    symbol_map: dict[str, str] | dict[str, int] = (
        CATEGORY_SYMBOLS_2D if dimensionality == 2 else CATEGORY_SYMBOLS_3D
    )

    if db_scatter_parameters.additional_symbol_map is not None:
        symbol_map.update(db_scatter_parameters.additional_symbol_map)  # type: ignore  # noqa: E501

    return symbol_map
