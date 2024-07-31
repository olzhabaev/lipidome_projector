"""Module concerning lipidome abundance changes."""

import logging

from itertools import permutations
from typing import cast, Literal, Self

import numpy as np
import pandas as pd
from pandas.core.api import Series as Series

from lipid_data_processing.lipidomes.base_df_wrapper import (
    BaseGroupedDfWrapper,
)


logger: logging.Logger = logging.getLogger(__name__)


class LipidomeAbundanceChanges(BaseGroupedDfWrapper):
    DEFAULT_INDEX_NAMES: tuple[str, str] = ("FROM", "TO")

    def __init__(self, df: pd.DataFrame, validate: bool = True):
        super().__init__(df, validate=validate)

        if validate:
            self._validate_levels(df)

        self._index_names: tuple[str, str] = cast(
            tuple[str, str], self.df.index.names
        )

    @classmethod
    def empty_from_lipids(
        cls,
        lipids: pd.Index,
        index_names: tuple[str, str] = DEFAULT_INDEX_NAMES,
        validate: bool = True,
    ) -> Self:
        index: pd.MultiIndex = pd.MultiIndex(
            levels=[[], []],
            codes=[[], []],
            names=index_names,
        )
        index.name = "INDEX"

        df: pd.DataFrame = pd.DataFrame(columns=lipids, index=index)

        return cls(df, validate=validate)

    @classmethod
    def pairwise_from_lipidome_abundances(
        cls,
        abundance_df: pd.DataFrame,
        index_names: tuple[str, str] = DEFAULT_INDEX_NAMES,
    ) -> Self:
        pairs: list[tuple[str, str]] = cls._generate_lipidome_pairs(
            abundance_df.index
        )

        pairwise_difference_df: pd.DataFrame = cls.compute_pairwise_change_df(
            abundance_df=abundance_df,
            pairs=pairs,
            index_names=index_names,
        )

        return cls(pairwise_difference_df)

    @property
    def from_lipidomes(self) -> pd.Index:
        return self.df.index.get_level_values(0)

    @property
    def to_lipidomes(self) -> pd.Index:
        return self.df.index.get_level_values(1)

    @property
    def lipids(self) -> pd.Index:
        return self.df.columns

    def add_pairwise_changes(
        self,
        abundance_df: pd.DataFrame,
        exists_handling: Literal["raise", "overwrite"] = "raise",
        validate: bool = True,
    ) -> None:
        if validate:
            if exists_handling not in ["raise", "overwrite"]:
                raise ValueError(f"Invalid exists_handling: {exists_handling}")

        pairs: list[tuple[str, str]] = self._generate_lipidome_pairs(
            abundance_df.index
        )

        pairwise_difference_df: pd.DataFrame = self.compute_pairwise_change_df(
            abundance_df=abundance_df,
            pairs=pairs,
            index_names=self._index_names,
        )

        if exists_handling == "raise":
            index_intersection: pd.MultiIndex = cast(
                pd.MultiIndex,
                self.df.index.intersection(pairwise_difference_df.index),
            )
            if not index_intersection.empty:
                raise ValueError(
                    f"Pairs {index_intersection} already exist in "
                    "pairwise difference df."
                )

        concat_df: pd.DataFrame = pd.concat(
            df for df in [self.df, pairwise_difference_df] if not df.empty
        )

        self._df = concat_df[~concat_df.index.duplicated(keep="last")]

    def add_change(
        self,
        abundance_df: pd.DataFrame,
        from_lipidome: str,
        to_lipidome: str,
        validate: bool = True,
    ) -> None:
        if validate:
            if from_lipidome == to_lipidome:
                raise ValueError(
                    f"Cannot add change for same lipidome: {from_lipidome}"
                )
            if (
                pd.MultiIndex.from_arrays(
                    [[from_lipidome], [to_lipidome]], names=[0, 1]
                )
                .isin(self.df.index)
                .all()
            ):
                raise ValueError(
                    f"Change for lipidome pair {from_lipidome} -> "
                    f"{to_lipidome} already exists."
                )
            if from_lipidome not in abundance_df.index:
                raise ValueError(
                    f"From lipidome '{from_lipidome}' not in "
                    "abundance df index."
                )
            if to_lipidome not in abundance_df.index:
                raise ValueError(
                    f"To lipidome '{to_lipidome}' not in abundance df index."
                )

        pair_change: pd.DataFrame = (
            self.compute_pair_change(abundance_df, from_lipidome, to_lipidome)
            .to_frame((from_lipidome, to_lipidome))
            .T
        )

        self._df = pd.concat(
            df for df in [self.df, pair_change] if not df.empty
        )

    def get_lipidome_pair_change(
        self,
        from_lipidome: str,
        to_lipidome: str,
        validate: bool = True,
    ) -> pd.Series:
        if validate:
            self.check_index_members_exist(
                pd.Index([from_lipidome, to_lipidome])
            )

        return self.df.loc[(from_lipidome, to_lipidome)].squeeze()  # type: ignore  # noqa: E501

    def get_subset(
        self,
        lipidomes: pd.Index | None = None,
        lipids: pd.Index | None = None,
        validate: bool = True,
    ) -> Self:
        return type(self)(
            self.get_index_member_subset_df(
                lipidomes, lipids, validate=validate
            )
        )

    def chk_lipidomes_exist(self, lipidomes: pd.Index) -> None:
        self.check_index_members_exist(lipidomes)

    def chk_lipids_exist(self, lipids: pd.Index) -> None:
        self._chk_columns_exist(lipids)

    @classmethod
    def compute_pairwise_change_df(
        cls,
        abundance_df: pd.DataFrame,
        pairs: list[tuple[str, str]],
        index_names: tuple[str, str] = DEFAULT_INDEX_NAMES,
    ) -> pd.DataFrame:
        pairwise_fc: dict[tuple[str, str], pd.Series] = {
            pair: cls.compute_pair_change(abundance_df, *pair)
            for pair in pairs
        }

        pairwise_fc_df: pd.DataFrame = pd.DataFrame(pairwise_fc).T

        pairwise_fc_df.index.set_names(index_names, inplace=True)

        return pairwise_fc_df

    @staticmethod
    def compute_pair_change(
        abundance_df: pd.DataFrame, from_lipidome: str, to_lipidome: str
    ) -> pd.Series:
        raise NotImplementedError

    @classmethod
    def _validate_levels(cls, df: pd.DataFrame) -> None:
        if df.index.nlevels != 2:
            raise ValueError(
                f"{cls} dataframe does not have two index levels. "
                f"Index levels: {df.index.nlevels}"
            )

    @staticmethod
    def _generate_lipidome_pairs(lipidomes: pd.Index) -> list[tuple[str, str]]:
        return list(permutations(lipidomes, 2))  # type: ignore


class LipidomeAbundanceDifferences(LipidomeAbundanceChanges):
    @staticmethod
    def compute_pair_change(
        abundance_df: pd.DataFrame, from_lipidome: str, to_lipidome: str
    ) -> pd.Series:
        return abundance_df.loc[from_lipidome].subtract(
            abundance_df.loc[to_lipidome]  # type: ignore
        )


class LipidomeAbundanceFC(LipidomeAbundanceChanges):
    @staticmethod
    def compute_pair_change(
        abundance_df: pd.DataFrame, from_lipidome: str, to_lipidome: str
    ) -> pd.Series:
        return abundance_df.loc[from_lipidome].divide(
            abundance_df.loc[to_lipidome]  # type: ignore
        )


class LipidomeAbundanceLog2FC(LipidomeAbundanceChanges):
    @staticmethod
    def compute_pair_change(
        abundance_df: pd.DataFrame, from_lipidome: str, to_lipidome: str
    ) -> Series:
        return (
            abundance_df.loc[from_lipidome]
            .divide(abundance_df.loc[to_lipidome])  # type: ignore
            .apply(np.log2)
        )


class AbundanceChangeStorage:
    def __init__(
        self,
        lipidomes: pd.Index,
        lipids: pd.Index,
        differences: LipidomeAbundanceDifferences | None = None,
        fcs: LipidomeAbundanceFC | None = None,
        log2fcs: LipidomeAbundanceLog2FC | None = None,
        validate: bool = True,
    ) -> None:
        if validate:
            self._validate_input(
                lipidomes=lipidomes,
                lipids=lipids,
                differences=differences,
                fcs=fcs,
                log2fcs=log2fcs,
            )

        self._lipidomes: pd.Index = lipidomes

        self._lipids: pd.Index = lipids

        self._differences: LipidomeAbundanceDifferences = (
            differences
            if differences is not None
            else LipidomeAbundanceDifferences.empty_from_lipids(
                lipids, validate=validate
            )
        )

        self._fcs: LipidomeAbundanceFC = (
            fcs
            if fcs is not None
            else LipidomeAbundanceFC.empty_from_lipids(
                lipids, validate=validate
            )
        )

        self._log2fcs: LipidomeAbundanceLog2FC = (
            log2fcs
            if log2fcs is not None
            else LipidomeAbundanceLog2FC.empty_from_lipids(
                lipids, validate=validate
            )
        )

    @classmethod
    def from_prepared_dfs(
        cls,
        lipidomes: pd.Index,
        lipids: pd.Index,
        differences_df: pd.DataFrame | None = None,
        fcs_df: pd.DataFrame | None = None,
        log2fcs_df: pd.DataFrame | None = None,
        validate: bool = True,
    ) -> Self:
        differences: LipidomeAbundanceDifferences | None = (
            LipidomeAbundanceDifferences(differences_df, validate=validate)
            if differences_df is not None
            else None
        )

        fcs: LipidomeAbundanceFC | None = (
            LipidomeAbundanceFC(fcs_df, validate=validate)
            if fcs_df is not None
            else None
        )

        log2fcs: LipidomeAbundanceLog2FC | None = (
            LipidomeAbundanceLog2FC(log2fcs_df, validate=validate)
            if log2fcs_df is not None
            else None
        )

        return cls(
            lipidomes=lipidomes,
            lipids=lipids,
            differences=differences,
            fcs=fcs,
            log2fcs=log2fcs,
            validate=validate,
        )

    @property
    def lipidomes(self) -> pd.Index:
        return self._lipidomes

    @property
    def lipids(self) -> pd.Index:
        return self._lipids

    @property
    def differences(self) -> LipidomeAbundanceDifferences:
        return self._differences

    @property
    def fcs(self) -> LipidomeAbundanceFC:
        return self._fcs

    @property
    def log2fcs(self) -> LipidomeAbundanceLog2FC:
        return self._log2fcs

    def add_pairwise_changes(
        self,
        abundance_change_type: Literal["difference", "fc", "log2fc"],
        abundance_df: pd.DataFrame,
        exists_handling: Literal["raise", "overwrite"] = "raise",
        validate: bool = True,
    ) -> None:
        self.get_abundance_changes(abundance_change_type).add_pairwise_changes(
            abundance_df, exists_handling, validate
        )

    def add_change(
        self,
        abundance_change_type: Literal["difference", "fc", "log2fc"],
        abundance_df: pd.DataFrame,
        from_lipidome: str,
        to_lipidome: str,
        validate: bool = True,
    ) -> None:
        self.get_abundance_changes(abundance_change_type).add_change(
            abundance_df, from_lipidome, to_lipidome, validate
        )

    def get_abundance_changes(
        self, abundance_change_type: Literal["difference", "fc", "log2fc"]
    ) -> LipidomeAbundanceChanges:
        if abundance_change_type == "difference":
            return self._differences
        elif abundance_change_type == "fc":
            return self._fcs
        elif abundance_change_type == "log2fc":
            return self._log2fcs
        else:
            raise ValueError(
                f"Invalid abundance change type: {abundance_change_type}"
            )

    def get_lipidome_pair_change(
        self,
        abundance_change_type: Literal["difference", "fc", "log2fc"],
        from_lipidome: str,
        to_lipidome: str,
        validate: bool = True,
    ) -> pd.Series:
        return self.get_abundance_changes(
            abundance_change_type
        ).get_lipidome_pair_change(from_lipidome, to_lipidome, validate)

    def get_subset(
        self,
        lipidomes: pd.Index | None = None,
        lipids: pd.Index | None = None,
        validate: bool = True,
    ) -> Self:
        if lipidomes is None:
            lipidomes = self.lipidomes
        if lipids is None:
            lipids = self.lipids

        return type(self)(
            lipidomes=lipidomes,
            lipids=lipids,
            differences=self.differences.get_subset(
                lipidomes, lipids, validate
            ),
            fcs=self.fcs.get_subset(lipidomes, lipids, validate),
            log2fcs=self.log2fcs.get_subset(lipidomes, lipids, validate),
            validate=False,
        )

    @classmethod
    def _validate_input(
        cls,
        lipidomes: pd.Index,
        lipids: pd.Index,
        differences: LipidomeAbundanceDifferences | None = None,
        fcs: LipidomeAbundanceFC | None = None,
        log2fcs: LipidomeAbundanceLog2FC | None = None,
    ) -> None:
        if differences is not None:
            cls._check_change_df_lipidomes(
                differences.from_lipidomes, lipidomes
            )
            cls._check_change_df_lipidomes(differences.to_lipidomes, lipidomes)
            cls._check_change_df_lipids(differences.lipids, lipids)
        if fcs is not None:
            cls._check_change_df_lipidomes(fcs.from_lipidomes, lipidomes)
            cls._check_change_df_lipidomes(fcs.to_lipidomes, lipidomes)
            cls._check_change_df_lipids(fcs.lipids, lipids)
        if log2fcs is not None:
            cls._check_change_df_lipidomes(log2fcs.from_lipidomes, lipidomes)
            cls._check_change_df_lipidomes(log2fcs.to_lipidomes, lipidomes)
            cls._check_change_df_lipids(log2fcs.lipids, lipids)

    @staticmethod
    def _check_change_df_lipidomes(
        df_lipidomes: pd.Index, lipidomes: pd.Index
    ) -> None:
        unknown_lipidomes: pd.Index = df_lipidomes.difference(lipidomes)
        if not unknown_lipidomes.empty:
            raise ValueError(
                f"Unknown lipidomes in change df: {unknown_lipidomes}"
            )

    @staticmethod
    def _check_change_df_lipids(df_lipids: pd.Index, lipids: pd.Index) -> None:
        unknown_lipids: pd.Index = df_lipids.difference(lipids)
        if not unknown_lipids.empty:
            raise ValueError(f"Unknown lipids in change df: {unknown_lipids}")
