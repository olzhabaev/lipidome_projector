"""Module concerning lipidome datasets."""

import logging

from io import StringIO
from pathlib import Path
from typing import Literal, Self

import pandas as pd

from lipid_data_processing.lipidomes.lipid_abundances import LipidAbundances
from lipid_data_processing.lipidomes.lipidome_abundances import (
    LipidomeAbundances,
)
from lipid_data_processing.lipidomes.lipidome_features import LipidomeFeatures
from lipid_data_processing.lipidomes.lipid_features import LipidFeatures
from lipid_data_processing.lipidomes.lipidome_abundance_changes import (
    AbundanceChangeStorage,
    LipidomeAbundanceChanges,
)


logger: logging.Logger = logging.getLogger(__name__)


class LipidomeDataset:
    def __init__(
        self,
        name: str,
        abundances: LipidomeAbundances,
        lipidome_features: LipidomeFeatures,
        lipid_features: LipidFeatures,
        abundance_change_storage: AbundanceChangeStorage | None = None,
        validate: bool = True,
    ):
        if validate:
            self._validate_input(
                lipidome_abundances=abundances,
                lipidome_features=lipidome_features,
                lipid_features=lipid_features,
                abundance_change_storage=abundance_change_storage,
            )

        self._name = name
        self._abundances: LipidomeAbundances = abundances
        self._lipidome_features: LipidomeFeatures = lipidome_features
        self._lipid_features: LipidFeatures = lipid_features
        self._abundance_change_storage: AbundanceChangeStorage = (
            abundance_change_storage
            if abundance_change_storage
            else AbundanceChangeStorage(
                self._abundances.lipidomes,
                self._abundances.lipids,
            )
        )

    @classmethod
    def from_csv_input(
        cls,
        name: str,
        abundances_csv_path_or_string_io: Path | StringIO,
        lipidome_features_csv_path_or_string_io: Path | StringIO,
        lipid_features_csv_path_or_string_io: Path | StringIO | None = None,
        validate: bool = True,
    ) -> Self:
        abundances: LipidomeAbundances = LipidomeAbundances.from_csv_input(
            abundances_csv_path_or_string_io,
            validate=validate,
        )
        lipidome_features: LipidomeFeatures = LipidomeFeatures.from_csv_input(
            lipidome_features_csv_path_or_string_io,
            validate=validate,
        )

        lipid_features: LipidFeatures = (
            LipidFeatures.from_csv_input(
                lipid_features_csv_path_or_string_io,
                validate=validate,
            )
            if lipid_features_csv_path_or_string_io is not None
            else LipidFeatures.empty_from_lipids(
                abundances.lipids.rename("INDEX"), validate=validate
            )
        )

        abundance_change_storage: AbundanceChangeStorage = (
            AbundanceChangeStorage.from_prepared_dfs(
                lipidomes=abundances.lipidomes,
                lipids=abundances.lipids,
            )
        )

        return cls(
            name=name,
            abundances=abundances,
            lipidome_features=lipidome_features,
            lipid_features=lipid_features,
            abundance_change_storage=abundance_change_storage,
            validate=validate,
        )

    @classmethod
    def from_prepared_dfs(
        cls,
        name: str,
        abundance_df: pd.DataFrame,
        lipidome_features_df: pd.DataFrame,
        lipid_features_df: pd.DataFrame,
        differences_df: pd.DataFrame | None = None,
        fcs_df: pd.DataFrame | None = None,
        log2fcs_df: pd.DataFrame | None = None,
        validate: bool = True,
    ) -> Self:
        lipidome_abundances: LipidomeAbundances = LipidomeAbundances(
            abundance_df,
            validate=validate,
        )

        lipidome_features: LipidomeFeatures = LipidomeFeatures(
            lipidome_features_df,
            validate=validate,
        )

        lipid_features: LipidFeatures = LipidFeatures(
            lipid_features_df,
            validate=validate,
        )

        abundance_change_storage: AbundanceChangeStorage = (
            AbundanceChangeStorage.from_prepared_dfs(
                lipidomes=lipidome_abundances.lipidomes,
                lipids=lipidome_abundances.lipids,
                differences_df=differences_df,
                fcs_df=fcs_df,
                log2fcs_df=log2fcs_df,
                validate=validate,
            )
        )

        return cls(
            name=name,
            abundances=lipidome_abundances,
            lipidome_features=lipidome_features,
            lipid_features=lipid_features,
            abundance_change_storage=abundance_change_storage,
            validate=False,
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def abundances(self) -> LipidomeAbundances:
        return self._abundances

    @property
    def lipidome_features(self) -> LipidomeFeatures:
        return self._lipidome_features

    @property
    def lipid_features(self) -> LipidFeatures:
        return self._lipid_features

    @property
    def abundance_change_storage(self) -> AbundanceChangeStorage:
        return self._abundance_change_storage

    @property
    def lipidomes(self) -> pd.Index:
        return self._abundances.lipidomes

    @property
    def lipids(self) -> pd.Index:
        return self._abundances.lipids

    @property
    def abundance_df(self) -> pd.DataFrame:
        return self._abundances.df

    @property
    def lipidome_features_df(self) -> pd.DataFrame:
        return self._lipidome_features.df

    @property
    def lipid_features_df(self) -> pd.DataFrame:
        return self._lipid_features.df

    def get_lipid_abundances(
        self,
        lipid: str,
        lipidomes: pd.Index | None = None,
    ) -> LipidAbundances:
        abundance_df: pd.DataFrame = self._abundances.get_subset(
            lipidomes, pd.Index([lipid]), validate=False
        ).df

        return LipidAbundances.from_series(abundance_df[lipid])

    def get_change_df(
        self, change_type: Literal["difference", "fc", "log2fc"]
    ) -> pd.DataFrame:
        abundance_changes: LipidomeAbundanceChanges = (
            self._abundance_change_storage.get_abundance_changes(change_type)
        )
        return abundance_changes.df

    def get_lipidome_pair_change(
        self,
        abundance_change_type: Literal["difference", "fc", "log2fc"],
        from_lipidome: str,
        to_lipidome: str,
        validate: bool = True,
    ) -> pd.Series:
        return self._abundance_change_storage.get_lipidome_pair_change(
            abundance_change_type, from_lipidome, to_lipidome, validate
        )

    def add_feature_in_place(
        self,
        name: str,
        values: pd.Series,
        overwrite: bool = False,
        validate: bool = True,
    ) -> None:
        self._lipidome_features.add_feature_in_place(
            name=name,
            values=values,
            overwrite=overwrite,
            validate=validate,
        )

    def add_pairwise_changes_in_place(
        self,
        abundance_change_type: Literal["difference", "fc", "log2fc"],
        lipidomes: pd.Index,
        exists_handling: Literal["raise", "overwrite"] = "raise",
        validate: bool = True,
    ) -> None:
        self.abundance_change_storage.add_pairwise_changes(
            abundance_change_type,
            self.abundance_df.loc[lipidomes],
            exists_handling=exists_handling,
            validate=validate,
        )

    def add_change_in_place(
        self,
        abundance_change_type: Literal["difference", "fc", "log2fc"],
        from_lipidome: str,
        to_lipidome: str,
        validate: bool = True,
    ) -> None:
        self.abundance_change_storage.add_change(
            abundance_change_type,
            self._abundances.df,
            from_lipidome,
            to_lipidome,
            validate,
        )

    def get_subset(
        self,
        lipidomes: pd.Index | None = None,
        lipids: pd.Index | None = None,
        name: str | None = None,
        validate: bool = True,
    ) -> Self:
        subset_abundances: LipidomeAbundances = self._abundances.get_subset(
            lipidomes, lipids, validate
        )
        subset_lipidome_features: LipidomeFeatures = (
            self._lipidome_features.get_subset(lipidomes, validate=validate)
        )
        subset_lipid_features: LipidFeatures = self._lipid_features.get_subset(
            lipids, validate=validate
        )
        subset_changes: AbundanceChangeStorage = (
            self._abundance_change_storage.get_subset(
                lipidomes, lipids, validate=False
            )
        )
        name = name if name is not None else self._name

        return type(self)(
            name=name,
            abundances=subset_abundances,
            lipidome_features=subset_lipidome_features,
            lipid_features=subset_lipid_features,
            abundance_change_storage=subset_changes,
            validate=False,
        )

    def gen_aggregations_by_lipidomes(
        self,
        lipidomes_list: list[pd.Index],
        operation: Literal["mean", "std"],
        group_names: list[str] | None = None,
        name: str | None = None,
        abundance_nan_handling: Literal["skip", "zero"] = "skip",
        validate: bool = True,
    ) -> Self:
        if group_names is None:
            group_names = self._gen_lipidome_group_names(
                lipidomes_list, operation, validate
            )

        aggregated_abundances: LipidomeAbundances = (
            self._abundances.gen_aggregations_by_lipidomes(
                lipidomes_list,
                operation,
                group_names,
                nan_handling=abundance_nan_handling,
                validate=validate,
            )
        )

        aggregated_lipidome_features: LipidomeFeatures = (
            self._lipidome_features.gen_aggregations_by_lipidomes(
                lipidomes_list,
                group_names,
                validate,
            )
        )

        name = name if name is not None else self._name

        return type(self)(
            name=name,
            abundances=aggregated_abundances,
            lipidome_features=aggregated_lipidome_features,
            lipid_features=self._lipid_features,
            abundance_change_storage=self.abundance_change_storage,
            validate=False,
        )

    def add_aggregations_by_lipidomes_in_place(
        self,
        lipidomes_list: list[pd.Index],
        operation: Literal["mean", "std"],
        group_names: list[str] | None = None,
        abundance_nan_handling: Literal["skip", "zero"] = "skip",
        validate: bool = True,
    ) -> None:
        if group_names is None:
            group_names = self._gen_lipidome_group_names(
                lipidomes_list, operation, validate
            )

        self._abundances.add_aggregations_by_lipidomes_in_place(
            lipidomes_list,
            operation,
            group_names,
            nan_handling=abundance_nan_handling,
            validate=validate,
        )

        self._lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list, group_names, validate
        )

    def gen_aggregations_by_features(
        self,
        features: list[str],
        operation: Literal["mean", "std"],
        name: str | None = None,
        abundance_nan_handling: Literal["skip", "zero"] = "skip",
        add_operation_prefix: bool = True,
        validate: bool = True,
    ) -> Self:
        lipidomes_list: list[pd.Index]
        group_names: list[str]
        lipidomes_list, group_names = self.gen_feature_aggregation_params(
            features, operation, add_operation_prefix, validate=validate
        )

        aggregated_dataset: Self = self.gen_aggregations_by_lipidomes(
            lipidomes_list,
            operation,
            group_names,
            name,
            abundance_nan_handling=abundance_nan_handling,
            validate=validate,
        )

        return aggregated_dataset

    def add_aggregations_by_features_in_place(
        self,
        features: list[str],
        operation: Literal["mean", "std"],
        abundance_nan_handling: Literal["skip", "zero"] = "skip",
        add_operation_prefix: bool = True,
        validate: bool = True,
    ) -> None:
        lipidomes_list: list[pd.Index]
        group_names: list[str]
        lipidomes_list, group_names = self.gen_feature_aggregation_params(
            features, operation, add_operation_prefix, validate=validate
        )

        self.add_aggregations_by_lipidomes_in_place(
            lipidomes_list,
            operation,
            group_names,
            abundance_nan_handling=abundance_nan_handling,
            validate=validate,
        )

    def gen_feature_aggregation_params(
        self,
        features: list[str],
        operation: Literal["mean", "std"],
        add_operation_prefix: bool,
        validate: bool = True,
    ) -> tuple[list[pd.Index], list[str]]:
        feature_product_lipidomes: list[tuple[pd.Index, list]] = (
            self._lipidome_features.get_feature_product_lipidomes(
                features, validate
            )
        )

        lipidomes_list: list[pd.Index] = [
            lipidome for lipidome, _ in feature_product_lipidomes
        ]

        group_names: list[str] = self._gen_feature_group_names(
            features, operation, add_operation_prefix, validate
        )

        return lipidomes_list, group_names

    def _gen_lipidome_group_names(
        self,
        lipidomes_list: list[pd.Index],
        operation: Literal["mean", "std"],
        validate: bool = True,
    ) -> list[str]:
        return [
            f"{operation} | {', '.join(lipidomes)}"
            for lipidomes in lipidomes_list
        ]

    def _gen_feature_group_names(
        self,
        features: list[str],
        operation: Literal["mean", "std"],
        add_operation_prefix: bool,
        validate: bool = True,
    ) -> list[str]:
        feature_product_lipidomes: list[tuple[pd.Index, list]] = (
            self._lipidome_features.get_feature_product_lipidomes(
                features, validate
            )
        )

        if add_operation_prefix:
            group_names: list[str] = [
                f"{operation} | {', '.join(feature_product)}"
                for _, feature_product in feature_product_lipidomes
            ]
        else:
            group_names = [
                f"{', '.join(feature_product)}"
                for _, feature_product in feature_product_lipidomes
            ]

        return group_names

    @classmethod
    def _validate_input(
        cls,
        lipidome_abundances: LipidomeAbundances,
        lipidome_features: LipidomeFeatures,
        lipid_features: LipidFeatures,
        abundance_change_storage: AbundanceChangeStorage | None,
    ) -> None:
        cls._validate_lipidomes(
            lipidome_abundances=lipidome_abundances,
            lipidome_features=lipidome_features,
        )

        cls._validate_lipids(
            lipidome_abundances=lipidome_abundances,
            lipid_features=lipid_features,
        )

        if abundance_change_storage is not None:
            cls._validate_changes(
                lipidome_abundances=lipidome_abundances,
                abundance_change_storage=abundance_change_storage,
            )

    @staticmethod
    def _validate_lipidomes(
        lipidome_abundances: LipidomeAbundances,
        lipidome_features: LipidomeFeatures,
    ) -> None:
        missing_abundance_lipidomes: pd.Index = (
            lipidome_features.lipidomes.difference(
                lipidome_abundances.lipidomes
            )
        )
        if not missing_abundance_lipidomes.empty:
            raise ValueError(
                f"Abundance lipidomes are missing feature lipidomes: "
                f"{missing_abundance_lipidomes}"
            )

        missing_feature_lipidomes: pd.Index = (
            lipidome_abundances.lipidomes.difference(
                lipidome_features.lipidomes
            )
        )
        if not missing_feature_lipidomes.empty:
            raise ValueError(
                f"Feature lipidomes are missing abundance lipidomes: "
                f"{missing_feature_lipidomes}"
            )

        if lipidome_abundances.index_name != lipidome_features.index_name:
            raise ValueError(
                f"Abundance and feature lipidomes do not have the same index "
                f"name: {lipidome_abundances.index_name} != "
                f"{lipidome_features.index_name}"
            )

    @staticmethod
    def _validate_lipids(
        lipidome_abundances: LipidomeAbundances,
        lipid_features: LipidFeatures,
    ) -> None:
        missing_abundance_lipids: pd.Index = lipid_features.lipids.difference(
            lipidome_abundances.lipids
        )
        if not missing_abundance_lipids.empty:
            raise ValueError(
                f"Abundance lipids are missing feature lipids: "
                f"{missing_abundance_lipids}"
            )

        missing_feature_lipids: pd.Index = (
            lipidome_abundances.lipids.difference(lipid_features.lipids)
        )
        if not missing_feature_lipids.empty:
            raise ValueError(
                f"Feature lipids are missing abundance lipids: "
                f"{missing_feature_lipids}"
            )

        missing_features_lipids: pd.Index = (
            lipidome_abundances.lipids.difference(  # noqa: E501
                lipid_features.lipids
            )
        )
        if not missing_features_lipids.empty:
            raise ValueError(
                "Lipid features are missing abundance lipids: "
                f"{missing_features_lipids}"
            )

    @staticmethod
    def _validate_changes(
        lipidome_abundances: LipidomeAbundances,
        abundance_change_storage: AbundanceChangeStorage,
    ) -> None:
        lipidome_difference: pd.Index = (
            lipidome_abundances.lipidomes.symmetric_difference(
                abundance_change_storage.lipidomes
            )
        )
        if not lipidome_difference.empty:
            raise ValueError(
                f"Difference between lipidome abundances and abundance "
                f"change lipidomes: {lipidome_difference}"
            )

        lipid_difference: pd.Index = (
            lipidome_abundances.lipids.symmetric_difference(
                abundance_change_storage.lipids
            )
        )
        if not lipid_difference.empty:
            raise ValueError(
                f"Difference between lipidome abundances and abundance "
                f"change lipids: {lipid_difference}"
            )
