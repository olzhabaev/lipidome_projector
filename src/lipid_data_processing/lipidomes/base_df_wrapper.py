"""Module concerning the base dataframe wrapper."""

import logging

from collections.abc import Callable
from functools import reduce
from io import StringIO
from pathlib import Path
from typing import Any, Literal, Self

import numpy as np
import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


class BaseDfWrapper:
    def __init__(self, df: pd.DataFrame, validate: bool = True) -> None:
        if validate:
            self.validate_df(df)

        self._df: pd.DataFrame = df

    @classmethod
    def from_csv_input(
        cls,
        csv_path_or_string_io: Path | StringIO,
        header: int = 0,
        index_col: int | list[int] = 0,
        dtype: dict[str, type] | None = None,
        validate: bool = True,
    ) -> Self:
        df: pd.DataFrame = pd.read_csv(
            csv_path_or_string_io,
            header=header,
            index_col=index_col,
            dtype=dtype,
        )

        return cls(df, validate=validate)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def index_name(self) -> str:
        return self.df.index.name

    def get_subset_df(
        self,
        index: pd.Index | None = None,
        columns: pd.Index | None = None,
        validate: bool = True,
    ) -> pd.DataFrame:
        if index is None:
            index = self.df.index
        elif validate:
            self._chk_indeces_exist(index)

        if columns is None:
            columns = self.df.columns
        elif validate:
            self._chk_columns_exist(columns)

        subset_df: pd.DataFrame = self.df.loc[index][columns]

        subset_df.index.name = self.df.index.name

        return subset_df

    def concat(self, other: Self, validate: bool = True) -> Self:
        if validate:
            self._validate_other_concat_compatibility(other)

        return type(self)(pd.concat([self.df, other.df]))

    def _validate_other_concat_compatibility(self, other: Self) -> None:
        differing_columns: pd.Index = self.df.columns.symmetric_difference(
            other.df.columns
        )
        if not differing_columns.empty:
            raise ValueError(
                f"Cannot concat {type(self).__name__} with differing columns: "
                f"{differing_columns}"
            )
        if self.df.index.nlevels != other.df.index.nlevels:
            raise ValueError(
                f"Cannot concat {type(self).__name__} with different index "
                f"levels."
            )
        index_intersection: pd.Index = self.df.index.intersection(
            other.df.index
        )
        if not index_intersection.empty:
            raise ValueError(
                f"Cannot concat {type(self).__name__} with overlapping index "
                f"members: {index_intersection}"
            )

    def add_aggregations_in_place(
        self,
        indeces_list: list[pd.Index],
        operation: Literal["mean", "std", "concat"],
        group_names: list[str] | None = None,
        prefix: str | None = None,
        skipna: bool = True,
        fillna: Any = None,
        validate: bool = True,
    ) -> None:
        if validate:
            self._validate_aggregation_operation(operation)
            self._validate_aggregation_indices_list(indeces_list, self._df)
            if group_names is not None:
                self._validate_aggregation_group_names(
                    self._df, group_names, indeces_list, True
                )

        agg_df: pd.DataFrame = self.gen_aggregations_df(
            self._df,
            indeces_list,
            operation,
            group_names,
            prefix,
            skipna,
            fillna,
        )

        self._df = pd.concat([self.df, agg_df])

    @classmethod
    def gen_aggregations_df(
        cls,
        df: pd.DataFrame,
        indeces_list: list[pd.Index],
        operation: Literal["mean", "std", "concat"],
        group_names: list[str] | None = None,
        prefix: str | None = None,
        skipna: bool = True,
        fillna: Any = None,
        validate: bool = True,
    ) -> pd.DataFrame:
        if validate:
            cls._validate_aggregation_operation(operation)
            cls._validate_aggregation_indices_list(indeces_list, df)
            if group_names is not None:
                cls._validate_aggregation_group_names(
                    df, group_names, indeces_list, False
                )

        df = cls._handle_nan(df, skipna, fillna)

        if group_names is None:
            prefix = prefix if prefix is not None else operation
            group_names = cls._gen_agg_group_names(indeces_list, prefix)

        aggregation_func: Callable[[pd.DataFrame, pd.Index], pd.Series] = (
            cls._det_aggregation(operation)
        )

        aggregations: dict[str, pd.Series] = {
            name: aggregation_func(df, indeces)
            for name, indeces in zip(group_names, indeces_list)
        }

        aggregation_df: pd.DataFrame = pd.DataFrame(aggregations).T

        aggregation_df.index.name = df.index.name

        return aggregation_df

    @staticmethod
    def _validate_aggregation_operation(
        operation: Literal["mean", "std", "concat"]
    ) -> None:
        if operation not in ["mean", "std", "concat"]:
            raise ValueError(
                f"Operation must be either 'mean' or 'std', but is {operation}"
            )

    @classmethod
    def _validate_aggregation_indices_list(
        cls, indices_list: list[pd.Index], df: pd.DataFrame
    ) -> None:
        if len(indices_list) == 0:
            raise ValueError("Indices list must not be empty.")

        for indices in indices_list:
            if len(indices) < 2:
                raise ValueError(
                    "Each indeces list must contain at least 2 indeces"
                )
        indices: pd.Index = reduce(
            lambda x, y: x.union(y), indices_list
        ).unique()

        missing_indices: pd.Index = indices.difference(df.index)
        if not missing_indices.empty:
            raise ValueError(
                f"{cls.__name__} dataframe does not contain indices: "
                f"{missing_indices}"
            )

    @classmethod
    def _validate_aggregation_group_names(
        cls,
        df: pd.DataFrame,
        group_names: list[str],
        indices_list: list[pd.Index],
        add_inplace: bool,
    ) -> None:
        if len(group_names) != len(indices_list):
            raise ValueError(
                "Number of group names must be equal to number of indeces."
            )

        duplicates: list[str] = [
            name for name in group_names if group_names.count(name) > 1
        ]
        if duplicates:
            raise ValueError(
                f"Group names must be unique, but duplicates were found: "
                f"{duplicates}"
            )

        if add_inplace:
            present_names: list[str] = [
                name for name in group_names if name in df.index
            ]
            if present_names:
                raise ValueError(
                    f"Group names already present in {cls.__name__} "
                    f"dataframe: {present_names}"
                )

    @staticmethod
    def _handle_nan(
        df: pd.DataFrame, skip: bool, fill_value: Any
    ) -> pd.DataFrame:
        if skip:
            return df
        else:
            return df.fillna(fill_value)

    @classmethod
    def _det_aggregation(
        cls, operation: Literal["mean", "std", "concat"]
    ) -> Callable[[pd.DataFrame, pd.Index], pd.Series]:
        if operation == "mean":
            return cls._gen_mean_aggregation
        elif operation == "std":
            return cls._gen_std_aggregation
        elif operation == "concat":
            return cls._gen_concat_aggregation
        else:
            raise ValueError(f"Unknown aggregation operation: '{operation}'")

    @staticmethod
    def _gen_mean_aggregation(
        df: pd.DataFrame, indeces: pd.Index
    ) -> pd.Series:
        return df.loc[indeces].mean(axis=0)

    @staticmethod
    def _gen_std_aggregation(df: pd.DataFrame, indeces: pd.Index) -> pd.Series:
        return df.loc[indeces].std(axis=0)

    @staticmethod
    def _gen_concat_aggregation(
        df: pd.DataFrame, indeces: pd.Index
    ) -> pd.Series:
        return df.loc[indeces].apply(
            lambda column: " | ".join(column.astype("str").unique()),
            axis="index",
        )

    @staticmethod
    def _gen_agg_group_names(
        indices: list[pd.Index], prefix: str
    ) -> list[str]:
        return [f"{prefix} | {', '.join(index)}" for index in indices]

    def _chk_indeces_exist(self, indices: pd.Index) -> None:
        missing_indices: pd.Index = indices.difference(self._df.index)
        if not missing_indices.empty:
            raise ValueError(
                f"Dataframe does not contain indices: {missing_indices}"
            )

    def _chk_columns_exist(self, columns: pd.Index) -> None:
        missing_columns: pd.Index = columns.difference(self._df.columns)
        if not missing_columns.empty:
            raise ValueError(
                f"Dataframe does not contain columns: {missing_columns}"
            )

    @classmethod
    def validate_df(cls, df: pd.DataFrame) -> None:
        """Validate the dataframe.
        :param df: Dataframe to validate.
        """
        cls._validate_indexes(df)

    @classmethod
    def _validate_indexes(cls, df: pd.DataFrame) -> None:
        cls._validate_duplicated_indices(df)
        cls._validate_duplicated_columns(df)
        cls._validate_non_string_column_names(df)
        cls._validate_non_string_index_names(df)
        cls._validate_multiindex_names(df)

    @staticmethod
    def _validate_duplicated_indices(df: pd.DataFrame) -> None:
        duplicated_indices: pd.Index = df.index[df.index.duplicated()]
        if not duplicated_indices.empty:
            raise ValueError(
                f"Dataframe contains duplicated indices: {duplicated_indices}"
            )

    @staticmethod
    def _validate_duplicated_columns(df: pd.DataFrame) -> None:
        duplicated_columns: pd.Index = df.columns[df.columns.duplicated()]
        if not duplicated_columns.empty:
            raise ValueError(
                f"Dataframe contains duplicated columns: {duplicated_columns}"
            )

    @staticmethod
    def _validate_non_string_column_names(df: pd.DataFrame) -> None:
        non_string_column_names: pd.Index = df.columns[
            [not isinstance(column, str) for column in df.columns]
        ]
        if not non_string_column_names.empty:
            raise ValueError(
                f"Dataframe contains non-string columns: "
                f"{non_string_column_names}"
            )

    @staticmethod
    def _validate_non_string_index_names(df: pd.DataFrame) -> None:
        if isinstance(df.index, pd.MultiIndex):
            non_string_index_names: pd.Index = df.index[
                [
                    any(not isinstance(level, str) for level in index)
                    for index in df.index
                ]
            ]
            if not non_string_index_names.empty:
                raise ValueError(
                    f"Dataframe contains non-string indices: "
                    f"{non_string_index_names}"
                )
        else:
            non_string_index_names: pd.Index = df.index[
                [not isinstance(index, str) for index in df.index]
            ]
            if not non_string_index_names.empty:
                raise ValueError(
                    f"Dataframe contains non-string indices: "
                    f"{non_string_index_names}"
                )

    @staticmethod
    def _validate_multiindex_names(df: pd.DataFrame) -> None:
        if isinstance(df.index, pd.MultiIndex):
            if None in df.index.names or "" in df.index.names:
                raise ValueError(
                    "Dataframe multiindex does has invalid names."
                )
        elif isinstance(df.index, pd.Index):
            if df.index.names in [None, ""]:
                raise ValueError("Dataframe index does not have a name.")


class BaseGroupedDfWrapper(BaseDfWrapper):
    def __init__(self, df: pd.DataFrame, validate: bool = True) -> None:
        super().__init__(df, validate=validate)
        if validate:
            self._validate_multiindex(df)

    def gen_single_index_df(
        self, new_index: pd.Index | None = None, validate: bool = True
    ) -> pd.DataFrame:
        if new_index is None:
            new_index = self.df.index.to_flat_index()
        elif validate:
            if isinstance(new_index, pd.MultiIndex):
                raise ValueError(
                    "New index must be a single index, not a multiindex."
                )
            if len(new_index) != len(self.df.index):
                raise ValueError(
                    f"New index must have same length as original index: "
                    f"{len(new_index)} != {len(self.df.index)}"
                )

        return self.df.set_index(new_index, inplace=False)

    def get_index_member_subset_df(
        self,
        index_members: pd.Index | None = None,
        columns: pd.Index | None = None,
        validate: bool = True,
    ) -> pd.DataFrame:
        if validate and index_members is not None:
            self.check_index_members_exist(index_members)

        members_present_index: pd.Index = (
            self._get_index_from_members(index_members)
            if index_members is not None
            else self.df.index
        )

        return self.get_subset_df(index=members_present_index, columns=columns)

    def check_index_members_exist(self, index_members: pd.Index) -> None:
        missing_members: pd.Index = index_members.difference(
            reduce(lambda x, y: x.union(y), self.df.index.levels)  # type: ignore  # noqa: E501
        )

        if not missing_members.empty:
            raise ValueError(
                f"{type(self).__name__} dataframe multiindex does not contain "
                f"members at levels: '{missing_members}'"
            )

    def _get_index_from_members(self, members: pd.Index) -> pd.Index:
        level_presence_masks: list[np.ndarray] = [
            self.df.index.get_level_values(i).isin(members)
            for i in range(self.df.index.nlevels)
        ]

        return self.df.index[np.all(level_presence_masks, axis=0)]

    @classmethod
    def _validate_multiindex(cls, df: pd.DataFrame) -> None:
        if not isinstance(df.index, pd.MultiIndex):
            raise ValueError(
                f"{cls.__name__} dataframe does not have a multiindex."
            )
