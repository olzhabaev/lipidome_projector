"""Module concerning scatter data objects."""

import logging

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScatterData:
    dataframe: pd.DataFrame

    vector_col_names: list[str]
    color_col_name: str | None = None
    symbol_col_name: str | None = None
    size_col_name: str | None = None
    hover_data_col_names: list[str] | None = None
    annotation_col_names: list[str] | None = None

    color_filter: list[str] | None = None
    symbol_filter: list[str] | None = None
    index_filter: pd.Index | None = None
    filtered_name: str = "FILTERED"

    dimensionality: Literal[2, 3] = field(init=False)

    color_column: pd.Series | None = field(init=False, default=None)
    symbol_column: pd.Series | None = field(init=False, default=None)
    size_column: pd.Series | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._chk_col_names()
        self._set_dimensionality()

        self._set_color_col()
        self._set_symbol_col()
        self._set_size_col()

    def _chk_col_names(self) -> None:
        if self.color_col_name is not None:
            if self.color_col_name not in self.dataframe.columns:
                raise ValueError(
                    f"Color column '{self.color_col_name}' "
                    "not in dataframe."
                )

        if self.symbol_col_name is not None:
            if self.symbol_col_name not in self.dataframe.columns:
                raise ValueError(
                    f"Symbol column '{self.symbol_col_name}' "
                    "not in dataframe."
                )

        if self.size_col_name is not None:
            if self.size_col_name not in self.dataframe.columns:
                raise ValueError(
                    f"Size column '{self.size_col_name}' " "not in dataframe."
                )

        if self.annotation_col_names is not None:
            if any(
                column not in self.dataframe.columns
                for column in self.annotation_col_names
            ):
                raise ValueError(
                    "Not all annotation column names in dataframe."
                )

        if self.hover_data_col_names is not None:
            if any(
                column not in self.dataframe.columns
                for column in self.hover_data_col_names
            ):
                raise ValueError(
                    "Not all hoverdata column names in dataframe."
                )

        if self.vector_col_names is not None:
            if any(
                column not in self.dataframe.columns
                for column in self.vector_col_names
            ):
                raise ValueError("Not all vector column names in dataframe.")

    def _set_dimensionality(self) -> None:
        dimensionality: int = len(self.vector_col_names)

        if not 2 <= dimensionality <= 3:
            raise ValueError("Vector dimensionality may only be 2 or 3.")

        object.__setattr__(self, "dimensionality", dimensionality)

    def _set_color_col(self) -> None:
        if self.color_col_name is not None:
            color_column: pd.Series | None = self._get_filtered_series(
                self.dataframe[self.color_col_name],
                self.color_filter,
                self.index_filter,
                self.filtered_name,
            )
            object.__setattr__(self, "color_column", color_column)

    def _set_symbol_col(self) -> None:
        if self.symbol_col_name is not None:
            object.__setattr__(
                self, "symbol_column", self.dataframe[self.symbol_col_name]
            )
        if self.symbol_col_name is not None:
            symbol_column: pd.Series | None = self._get_filtered_series(
                self.dataframe[self.symbol_col_name],
                self.symbol_filter,
                self.index_filter,
                self.filtered_name,
            )
            object.__setattr__(self, "symbol_column", symbol_column)

    def _set_size_col(self) -> None:
        if self.size_col_name is not None:
            object.__setattr__(
                self, "size_column", self.dataframe[self.size_col_name]
            )

    @staticmethod
    def _get_filtered_series(
        series: pd.Series,
        filter_values: list[str] | None,
        index_filter: pd.Index | None,
        filtered_name: str,
    ) -> pd.Series:
        filtered_series: pd.Series = series.copy()

        if filter_values is not None:
            if filtered_name in filtered_series.unique():
                raise ValueError(
                    f"Can not filter series as {filtered_name} "
                    "is already a value."
                )
            filter_map: dict[str, str] = {
                value: (filtered_name if value not in filter_values else value)
                for value in filtered_series.unique()
            }
            filtered_series = filtered_series.map(filter_map)

        if index_filter is not None:
            index_diff: pd.Index = filtered_series.index.difference(
                index_filter
            )
            filtered_series.loc[index_diff] = filtered_name

        return filtered_series
