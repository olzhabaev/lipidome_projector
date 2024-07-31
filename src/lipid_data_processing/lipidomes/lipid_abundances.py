"""Module concerning lipid abundances."""

import logging

from typing import Self

import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


class LipidAbundances:
    def __init__(
        self,
        abundance_df: pd.DataFrame,
        sample_column_name: str,
        abundance_column_name: str,
    ) -> None:
        self._validate_input(
            abundance_df,
            sample_column_name,
            abundance_column_name,
        )

        self._abundance_df = abundance_df
        self._sample_column_name = sample_column_name
        self._abundance_column_name = abundance_column_name

    def __repr__(self) -> str:
        return str(self.abundance_df)

    @property
    def abundance_df(self) -> pd.DataFrame:
        return self._abundance_df

    @property
    def sample_column_name(self) -> str:
        return self._sample_column_name

    @property
    def abundance_column_name(self) -> str:
        return self._abundance_column_name

    @staticmethod
    def _validate_input(
        lipid_abundances: pd.DataFrame,
        sample_column_name: str,
        abundance_column_name: str,
    ) -> None:
        if sample_column_name not in lipid_abundances.columns:
            raise ValueError(
                f"Column {sample_column_name} not found in dataframe."
            )
        if abundance_column_name not in lipid_abundances.columns:
            raise ValueError(
                f"Column {abundance_column_name} not found in dataframe."
            )

    @classmethod
    def from_series(cls, abundances: pd.Series) -> Self:
        if abundances.name is None:
            raise ValueError("Abundances series must have a name.")
        if abundances.index.name is None:
            raise ValueError("Abundances series index must have a name.")

        abundance_df: pd.DataFrame = abundances.to_frame().reset_index()

        lipid_abundances: Self = cls(
            abundance_df,
            sample_column_name=abundances.index.name,
            abundance_column_name=str(abundances.name),
        )

        return lipid_abundances

    @classmethod
    def from_dataframe(
        cls,
        abundance_df: pd.DataFrame,
        sample_column_name: str,
        abundance_column_name: str,
    ) -> Self:
        if sample_column_name not in abundance_df.columns:
            raise ValueError(
                f"Column {sample_column_name} not found in dataframe."
            )

        if abundance_column_name not in abundance_df.columns:
            raise ValueError(
                f"Column {abundance_column_name} not found in dataframe."
            )

        lipid_abundances: Self = cls(
            abundance_df,
            sample_column_name=sample_column_name,
            abundance_column_name=abundance_column_name,
        )

        return lipid_abundances
