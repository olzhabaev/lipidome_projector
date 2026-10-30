"""Module concerning the description of lipidomes."""

import logging

from dataclasses import dataclass
from typing import Literal, Self

import pandas as pd

from lipid_data_processing.lipidomes.lipidome_abundances import (
    LipidomeAbundances,
)
from lipid_data_processing.lipidomes.lipidome_abundance_changes import (
    AbundanceChangeStorage,
    LipidomeAbundanceDifferences,
    LipidomeAbundanceFC,
    LipidomeAbundanceLog2FC,
)
from lipid_data_processing.lipidomes.lipidome_features import LipidomeFeatures


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AbundanceRowDescription:
    sample_name: str
    series: pd.Series
    string: str

    def get_subset(self, indices: list[int]) -> Self:
        return type(self)(
            sample_name=self.sample_name,
            series=self.series.iloc[indices],  # type: ignore
            string=self.string,
        )


@dataclass(frozen=True)
class DatasetAbundancesDescription:
    lipids: pd.Index
    row_descriptions: list[AbundanceRowDescription]

    def __post_init__(self) -> None:
        for rd in self.row_descriptions:
            if not self.lipids.equals(rd.series.index):
                raise ValueError(
                    "Lipids do not match row description indices."
                )

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [rd.series for rd in self.row_descriptions],
        ).set_index(
            pd.Index(
                [rd.sample_name for rd in self.row_descriptions], name="INDEX"
            )
        )

    def to_str(self) -> str:
        header: str = (
            "INDEX," + ",".join([lipid for lipid in self.lipids]) + "\n"
        )

        abundances_str: str = header + "\n".join(
            [rd.string for rd in self.row_descriptions]
        )

        return abundances_str

    def get_subset(
        self, lipidome_indeces: list[int], lipid_indeces: list[int]
    ) -> Self:
        subset_abundances: list[AbundanceRowDescription] = [
            la.get_subset(lipid_indeces)
            for la in [self.row_descriptions[i] for i in lipidome_indeces]
        ]

        return type(self)(
            lipids=self.lipids[lipid_indeces],
            row_descriptions=subset_abundances,
        )


@dataclass(frozen=True)
class AbundancesAggregationTestData:
    lipidome_indices: list[pd.Index]
    group_names: list[str]
    lipidome_abundances: LipidomeAbundances
    operation: str
    nan_handling: Literal["skip", "zero"]


@dataclass(frozen=True)
class AbundancesChangeRowDescription:
    from_sample_name: str
    to_sample_name: str
    series: pd.Series


@dataclass(frozen=True)
class DatasetAbundancesChangeDescription:
    changes: list[AbundancesChangeRowDescription]

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [change.series for change in self.changes]
        ).set_index(
            pd.MultiIndex.from_tuples(
                [
                    (change.from_sample_name, change.to_sample_name)
                    for change in self.changes
                ],
                names=["FROM", "TO"],
            )
        )

    def get_lipidomes(self) -> pd.Index:
        df: pd.DataFrame = self.to_df()
        return pd.Index(
            pd.concat(
                [
                    df.index.get_level_values("FROM").to_series(),
                    df.index.get_level_values("TO").to_series(),
                ]
            )
        ).drop_duplicates()

    def to_differences(self) -> LipidomeAbundanceDifferences:
        return LipidomeAbundanceDifferences(self.to_df())

    def to_fc(self) -> LipidomeAbundanceFC:
        return LipidomeAbundanceFC(self.to_df())

    def to_log2fc(self) -> LipidomeAbundanceLog2FC:
        return LipidomeAbundanceLog2FC(self.to_df())


@dataclass(frozen=True)
class AbundanceChangeStorageDescription:
    lipidomes: pd.Index
    lipids: pd.Index
    differences_desc: DatasetAbundancesChangeDescription
    fc_desc: DatasetAbundancesChangeDescription
    log2fc_desc: DatasetAbundancesChangeDescription

    def to_storage(self) -> AbundanceChangeStorage:
        return AbundanceChangeStorage(
            lipidomes=self.lipidomes,
            lipids=self.lipids,
            differences=self.differences_desc.to_differences(),
            fcs=self.fc_desc.to_fc(),
            log2fcs=self.log2fc_desc.to_log2fc(),
        )


@dataclass(frozen=True)
class LipidomeFeaturesRowDescription:
    sample_name: str
    series: pd.Series
    string: str


@dataclass(frozen=True)
class DatasetLipidomeFeaturesDescription:
    features: list[LipidomeFeaturesRowDescription]

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame([rd.series for rd in self.features]).set_index(
            pd.Index([rd.sample_name for rd in self.features], name="INDEX")
        )

    def get_subset(self, lipidome_indeces: list[int]) -> Self:
        return type(self)(
            features=[self.features[i] for i in lipidome_indeces],
        )


@dataclass(frozen=True)
class LipidomeFeaturesAggregationTestData:
    lipidome_indeces: list[pd.Index]
    group_names: list[str]
    lipidome_features: LipidomeFeatures


@dataclass(frozen=True)
class LipidomeFeaturesAddFeatureTestData:
    lipidome_features: LipidomeFeatures
    updated_lipidome_features: LipidomeFeatures
    feature_name: str
    feature_values: pd.Series
    overwrite: bool


@dataclass(frozen=True)
class LipidomeDatasetDescription:
    name: str
    abundances: DatasetAbundancesDescription
    abundance_change_storage: AbundanceChangeStorageDescription
    lipidome_features: DatasetLipidomeFeaturesDescription
