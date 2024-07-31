"""Module concerning lipidome lipid abundances."""

import logging

from collections import defaultdict
from io import StringIO
from pathlib import Path
from typing import Literal, Self

import pandas as pd

from lipid_data_processing.lipidomes.base_df_wrapper import BaseDfWrapper


logger: logging.Logger = logging.getLogger(__name__)


class LipidomeAbundances(BaseDfWrapper):
    def __init__(
        self,
        df: pd.DataFrame,
        validate: bool = True,
    ):
        super().__init__(df, validate=validate)

        if validate:
            self._validate_not_empty(df)
            self._validate_dtype(df)
            self._validate_values(df)

    @classmethod
    def from_csv_input(
        cls,
        csv_path_string_io: Path | StringIO,
        validate: bool = True,
    ) -> Self:
        dtype: dict = defaultdict(lambda: float)
        dtype[0] = str

        return super().from_csv_input(
            csv_path_or_string_io=csv_path_string_io,
            header=0,
            index_col=0,
            dtype=dtype,
            validate=validate,
        )

    @property
    def lipidomes(self) -> pd.Index:
        return self.df.index

    @property
    def lipids(self) -> pd.Index:
        return self.df.columns

    def chk_lipidomes_exist(self, lipidomes: pd.Index) -> None:
        self._chk_indeces_exist(lipidomes)

    def chk_lipids_exist(self, lipids: pd.Index) -> None:
        self._chk_columns_exist(lipids)

    def get_subset(
        self,
        lipidomes: pd.Index | None = None,
        lipids: pd.Index | None = None,
        validate: bool = True,
    ) -> Self:
        subset_df: pd.DataFrame = self.get_subset_df(
            index=lipidomes, columns=lipids, validate=validate
        )

        return type(self)(subset_df, validate=False)

    def gen_aggregations_by_lipidomes(
        self,
        lipidomes_list: list[pd.Index],
        operation: Literal["mean", "std"],
        group_names: list[str] | None = None,
        nan_handling: Literal["skip", "zero"] = "skip",
        validate: bool = True,
    ) -> Self:
        self._validate_aggregation_operation(operation)
        skipna: bool
        fillna: float | None
        skipna, fillna = self._get_aggregation_nan_params(nan_handling)

        aggregation_df: pd.DataFrame = self.gen_aggregations_df(
            df=self.df,
            indeces_list=lipidomes_list,
            operation=operation,
            group_names=group_names,
            validate=validate,
            skipna=skipna,
            fillna=fillna,
        )

        return type(self)(aggregation_df, validate=False)

    def add_aggregations_by_lipidomes_in_place(
        self,
        lipidomes_list: list[pd.Index],
        operation: Literal["mean", "std"],
        group_names: list[str] | None = None,
        nan_handling: Literal["skip", "zero"] = "skip",
        validate: bool = True,
    ) -> None:
        self._validate_aggregation_operation(operation)
        skipna: bool
        fillna: float | None
        skipna, fillna = self._get_aggregation_nan_params(nan_handling)

        aggregation_df: pd.DataFrame = self.gen_aggregations_df(
            df=self.df,
            indeces_list=lipidomes_list,
            operation=operation,
            group_names=group_names,
            validate=validate,
            skipna=skipna,
            fillna=fillna,
        )

        self._df = pd.concat([self.df, aggregation_df])

    @staticmethod
    def _get_aggregation_nan_params(
        nan_handling: Literal["skip", "zero"]
    ) -> tuple[bool, float | None]:
        if nan_handling == "skip":
            skipna: bool = True
            fillna: float | None = None
        elif nan_handling == "zero":
            skipna: bool = False
            fillna: float | None = 0.0
        else:
            raise ValueError(
                f"nan_handling must be either 'skip' or 'zero', but is "
                f"{nan_handling}"
            )

        return skipna, fillna

    @staticmethod
    def _validate_aggregation_operation(
        operation: Literal["mean", "std"]
    ) -> None:
        if operation not in ["mean", "std"]:
            raise ValueError(
                f"Operation must be either 'mean' or 'std', but is {operation}"
            )

    @classmethod
    def _validate_not_empty(cls, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError(f"{cls.__name__} dataframe is empty.")

    @classmethod
    def _validate_dtype(cls, df: pd.DataFrame) -> None:
        non_float_columns: pd.Index = df.columns[
            ~df.dtypes.map(pd.api.types.is_numeric_dtype)
        ]
        if not non_float_columns.empty:
            column_dtype_map: dict[str, str] = {
                column: str(df[column].dtype) for column in non_float_columns
            }
            raise ValueError(
                f"{cls.__name__} dataframe contains non-float columns: "
                f"{column_dtype_map}"
            )

    @classmethod
    def _validate_values(cls, df: pd.DataFrame) -> None:
        if (df.values < 0).any():
            raise ValueError(
                f"{cls.__name__} dataframe contains negative values."
            )
