"""Module concerning the testing of lipidome abundance changes."""

import logging

from typing import Literal

import pandas as pd
import pytest

from lipid_data_processing.lipidomes.lipidome_abundance_changes import (
    LipidomeAbundanceDifferences,
    LipidomeAbundanceFC,
    LipidomeAbundanceLog2FC,
    AbundanceChangeStorage,
)


logger: logging.Logger = logging.getLogger(__name__)


def test_differences_add_pairwise_changes(
    ld_0_differences_subset_abundances_df_0: pd.DataFrame,
    ld_0_differences_subset_df_0: pd.DataFrame,
    ld_0_lipids: pd.Index,
) -> None:
    test_differences: LipidomeAbundanceDifferences = (
        LipidomeAbundanceDifferences.empty_from_lipids(ld_0_lipids)
    )

    test_differences.add_pairwise_changes(
        ld_0_differences_subset_abundances_df_0
    )

    pd.testing.assert_frame_equal(
        ld_0_differences_subset_df_0, test_differences.df
    )


def test_differences_add_pairwise_changes_exists_raise(
    ld_0_differences_subset_abundances_df_0: pd.DataFrame,
    ld_0_lipids: pd.Index,
) -> None:
    test_differences: LipidomeAbundanceDifferences = (
        LipidomeAbundanceDifferences.empty_from_lipids(ld_0_lipids)
    )

    test_differences.add_pairwise_changes(
        ld_0_differences_subset_abundances_df_0
    )

    with pytest.raises(ValueError, match="exist"):
        test_differences.add_pairwise_changes(
            ld_0_differences_subset_abundances_df_0,
            exists_handling="raise",
        )


def test_fc_add_pairwise_changes(
    ld_0_fc_subset_abundances_df_0: pd.DataFrame,
    ld_0_fc_subset_df_0: pd.DataFrame,
    ld_0_lipids: pd.Index,
) -> None:
    test_fc: LipidomeAbundanceFC = LipidomeAbundanceFC.empty_from_lipids(
        ld_0_lipids
    )

    test_fc.add_pairwise_changes(ld_0_fc_subset_abundances_df_0)

    pd.testing.assert_frame_equal(ld_0_fc_subset_df_0, test_fc.df)


def test_log2fc_add_pairwise_changes(
    ld_0_log2fc_subset_abundances_df_0: pd.DataFrame,
    ld_0_log2fc_subset_df_0: pd.DataFrame,
    ld_0_lipids: pd.Index,
) -> None:
    test_log2fc: LipidomeAbundanceLog2FC = (
        LipidomeAbundanceLog2FC.empty_from_lipids(ld_0_lipids)
    )

    test_log2fc.add_pairwise_changes(ld_0_log2fc_subset_abundances_df_0)

    pd.testing.assert_frame_equal(ld_0_log2fc_subset_df_0, test_log2fc.df)


@pytest.mark.parametrize(
    "method_name,input_df_name,target_df_name",
    [
        (
            "difference",
            "ld_0_differences_subset_abundances_df_0",
            "ld_0_differences_subset_df_0",
        ),
        ("fc", "ld_0_fc_subset_abundances_df_0", "ld_0_fc_subset_df_0"),
        (
            "log2fc",
            "ld_0_log2fc_subset_abundances_df_0",
            "ld_0_log2fc_subset_df_0",
        ),
    ],
)
def test_storage_add_pairwise_changes(
    method_name: Literal["difference", "fc", "log2fc"],
    input_df_name: str,
    target_df_name: str,
    ld_0_lipidome_sample_names: pd.Index,
    ld_0_lipids: pd.Index,
    request: pytest.FixtureRequest,
) -> None:
    input_df: pd.DataFrame = request.getfixturevalue(input_df_name)
    target_df: pd.DataFrame = request.getfixturevalue(target_df_name)

    test_storage: AbundanceChangeStorage = AbundanceChangeStorage(
        lipidomes=ld_0_lipidome_sample_names, lipids=ld_0_lipids
    )

    test_storage.add_pairwise_changes(method_name, input_df)

    pd.testing.assert_frame_equal(
        target_df, test_storage.get_abundance_changes(method_name).df
    )
