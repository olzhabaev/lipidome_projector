"""Module concerning the testing of lipidome datasets."""

import logging

from io import StringIO

import pandas as pd
import pytest

from lipid_data_processing.lipidomes.lipidome_abundances import (
    LipidomeAbundances,
)
from lipid_data_processing.lipidomes.lipidome_abundance_changes import (
    AbundanceChangeStorage,
)
from lipid_data_processing.lipidomes.lipidome_dataset import (
    LipidomeDataset,
)
from lipid_data_processing.lipidomes.lipid_features import LipidFeatures
from lipid_data_processing.lipidomes.lipidome_features import LipidomeFeatures


logger: logging.Logger = logging.getLogger(__name__)


def test_lipidome_dataset_creation(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundance_change_storage: AbundanceChangeStorage,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty: LipidFeatures,
) -> None:
    lipidome_ds: LipidomeDataset = LipidomeDataset(
        name="test_name",
        abundances=ld_0_abundances,
        abundance_change_storage=ld_0_abundance_change_storage,
        lipidome_features=ld_0_lipidome_features,
        lipid_features=ld_0_lipid_features_empty,
    )

    assert lipidome_ds.name == "test_name"


def test_lipidome_dataset_creation_lipid_mismatch_failure(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundance_change_storage: AbundanceChangeStorage,
    ld_0_lipidome_features: LipidomeFeatures,
) -> None:
    new_lipid_features: LipidFeatures = LipidFeatures.empty_from_lipids(
        pd.Index(["new_lipid_1", "new_lipid_2"])
    )

    with pytest.raises(ValueError, match="new_lipid_1"):
        LipidomeDataset(
            name="test_name",
            abundances=ld_0_abundances,
            abundance_change_storage=ld_0_abundance_change_storage,
            lipidome_features=ld_0_lipidome_features,
            lipid_features=new_lipid_features,
        )


def test_lipidome_dataset_creation_lipidome_mismatch_failure(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundance_change_storage: AbundanceChangeStorage,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty: LipidFeatures,
) -> None:
    new_lipidome_features: LipidomeFeatures = LipidomeFeatures(
        ld_0_lipidome_features.df[0:-1]
    )

    with pytest.raises(ValueError, match="missing abundance lipidomes"):
        LipidomeDataset(
            name="test_name",
            abundances=ld_0_abundances,
            abundance_change_storage=ld_0_abundance_change_storage,
            lipidome_features=new_lipidome_features,
            lipid_features=ld_0_lipid_features_empty,
        )


def test_lipidome_dataset_creation_abundance_mismatch_failure(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundance_change_storage: AbundanceChangeStorage,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty: LipidFeatures,
) -> None:
    new_abundances: LipidomeAbundances = LipidomeAbundances(
        ld_0_abundances.df[0:-1]
    )

    with pytest.raises(ValueError, match="missing feature lipidomes"):
        LipidomeDataset(
            name="test_name",
            abundances=new_abundances,
            abundance_change_storage=ld_0_abundance_change_storage,
            lipidome_features=ld_0_lipidome_features,
            lipid_features=ld_0_lipid_features_empty,
        )


def test_lipidome_dataset_creation_changes_lipidome_difference_failure(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundance_change_storage: AbundanceChangeStorage,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty: LipidFeatures,
) -> None:
    new_abundance_change_storage: AbundanceChangeStorage = (
        AbundanceChangeStorage(
            lipidomes=ld_0_abundance_change_storage.lipidomes[0:-1],
            lipids=ld_0_abundance_change_storage.lipids,
        )
    )

    with pytest.raises(ValueError, match="change lipidomes"):
        LipidomeDataset(
            name="test_name",
            abundances=ld_0_abundances,
            abundance_change_storage=new_abundance_change_storage,
            lipidome_features=ld_0_lipidome_features,
            lipid_features=ld_0_lipid_features_empty,
        )


def test_lipidome_dataset_creation_changes_lipid_difference_failure(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundance_change_storage: AbundanceChangeStorage,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty: LipidFeatures,
) -> None:
    new_abundance_change_storage: AbundanceChangeStorage = (
        AbundanceChangeStorage(
            lipidomes=ld_0_abundance_change_storage.lipidomes,
            lipids=ld_0_abundance_change_storage.lipids[0:-1],
        )
    )

    with pytest.raises(ValueError, match="change lipids"):
        LipidomeDataset(
            name="test_name",
            abundances=ld_0_abundances,
            abundance_change_storage=new_abundance_change_storage,
            lipidome_features=ld_0_lipidome_features,
            lipid_features=ld_0_lipid_features_empty,
        )


def test_lipidome_dataset_from_csv_input(
    ld_0_abundances_str_io: StringIO,
    ld_0_abundances: LipidomeAbundances,
    ld_0_lipidome_features_str_io: StringIO,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty: LipidFeatures,
) -> None:
    lipidome_ds: LipidomeDataset = LipidomeDataset.from_csv_input(
        name="test_name",
        abundances_csv_path_or_string_io=ld_0_abundances_str_io,
        lipidome_features_csv_path_or_string_io=ld_0_lipidome_features_str_io,
    )

    assert lipidome_ds.name == "test_name"
    assert lipidome_ds.abundances.df.equals(ld_0_abundances.df)
    assert lipidome_ds.lipidome_features.df.equals(ld_0_lipidome_features.df)
    assert lipidome_ds.lipid_features.df.equals(ld_0_lipid_features_empty.df)


def test_lipidome_dataset_from_prepared_dfs(
    ld_0_abundances_df: pd.DataFrame,
    ld_0_abundances: LipidomeAbundances,
    ld_0_lipidome_features_df: pd.DataFrame,
    ld_0_lipidome_features: LipidomeFeatures,
    ld_0_lipid_features_empty_df: pd.DataFrame,
    ld_0_lipid_features_empty: LipidFeatures,
    ld_0_differences_subset_df_0: pd.DataFrame,
    ld_0_fc_subset_df_0: pd.DataFrame,
    ld_0_log2fc_subset_df_0: pd.DataFrame,
) -> None:
    lipidome_ds: LipidomeDataset = LipidomeDataset.from_prepared_dfs(
        name="test_name",
        abundance_df=ld_0_abundances_df,
        lipidome_features_df=ld_0_lipidome_features_df,
        lipid_features_df=ld_0_lipid_features_empty_df,
        differences_df=ld_0_differences_subset_df_0,
        fcs_df=ld_0_fc_subset_df_0,
        log2fcs_df=ld_0_log2fc_subset_df_0,
    )

    assert lipidome_ds.name == "test_name"
    assert lipidome_ds.abundances.df.equals(ld_0_abundances.df)
    assert lipidome_ds.lipidome_features.df.equals(ld_0_lipidome_features.df)
    assert lipidome_ds.lipid_features.df.equals(ld_0_lipid_features_empty.df)
    assert lipidome_ds.abundance_change_storage.differences.df.equals(
        ld_0_differences_subset_df_0
    )
    assert lipidome_ds.abundance_change_storage.fcs.df.equals(
        ld_0_fc_subset_df_0
    )
    assert lipidome_ds.abundance_change_storage.log2fcs.df.equals(
        ld_0_log2fc_subset_df_0
    )
