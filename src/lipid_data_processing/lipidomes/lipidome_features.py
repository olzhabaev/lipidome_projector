"""Module concerning lipidome features."""

import logging

from itertools import product
from typing import Self

import numpy as np
import pandas as pd

from lipid_data_processing.lipidomes.base_df_wrapper import (
    BaseDfWrapper,
    BaseGroupedDfWrapper,
)


logger: logging.Logger = logging.getLogger(__name__)


class LipidomeFeatures(BaseDfWrapper):
    def __init__(
        self,
        df: pd.DataFrame,
        validate: bool = True,
    ):
        super().__init__(df, validate=validate)

    def get_subset(
        self,
        lipidomes: pd.Index | None = None,
        features: pd.Index | None = None,
        validate: bool = True,
    ) -> Self:
        subset_df: pd.DataFrame = self.get_subset_df(
            index=lipidomes, columns=features, validate=validate
        )

        return type(self)(subset_df, validate=False)

    def chk_lipidomes_exist(self, lipidomes: pd.Index) -> None:
        self._chk_indeces_exist(lipidomes)

    def add_feature(
        self,
        name: str,
        values: pd.Series,
        overwrite: bool = False,
        validate: bool = True,
    ) -> Self:
        if validate:
            self._chk_add_feature_input(name, values, overwrite)

        return type(self)(self.df.assign(**{name: values}), validate=False)

    def add_feature_in_place(
        self,
        name: str,
        values: pd.Series,
        overwrite: bool = False,
        validate: bool = True,
    ) -> None:
        if validate:
            self._chk_add_feature_input(name, values, overwrite)

        self._df[name] = values

    def gen_aggregations_by_lipidomes(
        self,
        lipidomes_list: list[pd.Index],
        group_names: list[str] | None = None,
        validate: bool = True,
    ) -> Self:
        aggregation_df: pd.DataFrame = self.gen_aggregations_df(
            df=self.df,
            indeces_list=lipidomes_list,
            operation="concat",
            group_names=group_names,
            validate=validate,
        )

        return type(self)(aggregation_df, validate=False)

    def add_aggregations_by_lipidomes_in_place(
        self,
        lipidomes_list: list[pd.Index],
        group_names: list[str] | None = None,
        validate: bool = True,
    ) -> None:
        self.add_aggregations_in_place(
            indeces_list=lipidomes_list,
            operation="concat",
            group_names=group_names,
            validate=validate,
        )

    def get_feature_product_lipidomes(
        self, features: list[str], validate: bool = True
    ) -> list[tuple[pd.Index, list]]:
        if validate:
            self._chk_columns_exist(pd.Index(features))

        features_product: list = list(
            product(
                *[self.df[feature].unique().tolist() for feature in features]
            )
        )

        index_masks: list[np.ndarray] = [
            np.logical_and.reduce(
                list(
                    (self.df[feature] == value)
                    for feature, value in zip(features, feature_values)
                )
            )
            for feature_values in features_product
        ]

        indeces: list[pd.Index] = [
            self.df.index[index_mask] for index_mask in index_masks
        ]

        return list(zip(indeces, features_product))

    @property
    def lipidomes(self) -> pd.Index:
        return self.df.index

    @property
    def features(self) -> pd.Index:
        return self.df.columns

    def _chk_add_feature_input(
        self, name: str, values: pd.Series, overwrite: bool
    ) -> None:
        if name in self.df.columns and not overwrite:
            raise ValueError(
                f"Feature '{name}' already exists in the dataframe."
            )
        if not values.index.equals(self.df.index):
            raise ValueError(
                "Index of values does not match index of dataframe."
            )


class GroupedLipidomeFeatures(BaseGroupedDfWrapper):
    def __init__(self, df: pd.DataFrame, validate: bool = True):
        super().__init__(df, validate=validate)

    @classmethod
    def from_lipidome_groups(
        cls,
        lipidome_features: LipidomeFeatures,
        lipidome_groups: list[pd.Index],
        validate: bool = True,
    ) -> Self:
        if validate:
            cls._validate_features_groups_input(
                lipidome_features, lipidome_groups
            )

        grouped_feature_df: pd.DataFrame = cls._get_grouped_feature_df(
            lipidome_features, lipidome_groups
        )

        return cls(grouped_feature_df, validate=False)

    @property
    def lipidomes(self) -> pd.MultiIndex:
        return self.df.index  # type: ignore

    @property
    def features(self) -> pd.Index:
        return self.df.columns

    def get_lipidome_subset(
        self, lipidomes: pd.Index, validate: bool = True
    ) -> Self:
        return type(self)(
            self.get_index_member_subset_df(lipidomes, validate=validate),
            validate=False,
        )

    def gen_non_grouped_lipidome_features(
        self, new_group_names: list[str] | None = None, validate: bool = True
    ) -> Self:
        new_index: pd.Index | None = (
            pd.Index(new_group_names) if new_group_names is not None else None
        )

        return type(self)(
            self.gen_single_index_df(new_index, validate), validate=False
        )

    @staticmethod
    def _validate_features_groups_input(
        lipidome_features: LipidomeFeatures,
        lipidome_groups: list[pd.Index],
    ) -> None:
        lipidomes: pd.Index = pd.Index(
            set(lipidome for group in lipidome_groups for lipidome in group)
        )
        lipidome_features.chk_lipidomes_exist(lipidomes=lipidomes)

    @classmethod
    def _get_grouped_feature_df(
        cls,
        lipidome_features: LipidomeFeatures,
        lipidome_groups: list[pd.Index],
    ) -> pd.DataFrame:
        grouped_feature_rows: dict[tuple[str, ...], pd.Series] = {
            tuple(group): cls._gen_group_feature_row(
                group_df=lipidome_features.df.loc[group]
            )
            for group in lipidome_groups
        }

        return pd.DataFrame(grouped_feature_rows).T

    @staticmethod
    def _gen_group_feature_row(group_df: pd.DataFrame) -> pd.Series:
        return group_df.apply(
            lambda column: " | ".join(column.unique()), axis="index"
        )
