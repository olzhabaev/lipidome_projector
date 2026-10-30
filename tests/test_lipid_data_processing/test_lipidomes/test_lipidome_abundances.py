"""Module concerning the testing of lipidome abundances."""

import logging

from io import StringIO
from pathlib import Path
from typing import cast, Literal

import pandas as pd
import pytest

from lipid_data_processing.lipidomes.lipidome_abundances import (
    LipidomeAbundances,
)
from tests.test_lipid_data_processing.util.lipidome_description import (
    AbundancesAggregationTestData,
)

logger: logging.Logger = logging.getLogger(__name__)


def test_lipidome_abundances_creation_success(
    ld_0_abundances_df: pd.DataFrame,
) -> None:
    lipidome_abundances: LipidomeAbundances = LipidomeAbundances(
        ld_0_abundances_df
    )

    pd.testing.assert_frame_equal(lipidome_abundances.df, ld_0_abundances_df)


def test_lipidome_abundances_creation_failure_empty() -> None:
    with pytest.raises(ValueError, match="empty"):
        LipidomeAbundances(df=pd.DataFrame())


def test_lipidome_abundances_creation_failure_duplicated_index(
    ld_0_abundances_df: pd.DataFrame,
) -> None:
    duplicated_df: pd.DataFrame = pd.concat(
        [ld_0_abundances_df, ld_0_abundances_df], axis="index"
    )
    with pytest.raises(ValueError, match="duplicated indices"):
        LipidomeAbundances(duplicated_df)


def test_lipidome_abundances_creation_failure_duplicated_columns(
    ld_0_abundances_df: pd.DataFrame,
) -> None:
    duplicated_columns_df: pd.DataFrame = pd.concat(
        [ld_0_abundances_df, ld_0_abundances_df], axis="columns"
    )
    with pytest.raises(ValueError, match="duplicated columns"):
        LipidomeAbundances(duplicated_columns_df)


def test_lipidome_abundances_creation_from_str_io(
    ld_0_abundances_df: pd.DataFrame, ld_0_abundances_str_io: StringIO
) -> None:
    lipidome_abundances: LipidomeAbundances = (
        LipidomeAbundances.from_csv_input(
            csv_path_string_io=ld_0_abundances_str_io
        )
    )

    pd.testing.assert_frame_equal(ld_0_abundances_df, lipidome_abundances.df)


def test_lipidome_abundances_creation_from_path(
    ld_0_abundances_df: pd.DataFrame, ld_0_abundances_tmp_file_path: Path
) -> None:
    lipidome_abundances: LipidomeAbundances = (
        LipidomeAbundances.from_csv_input(
            csv_path_string_io=ld_0_abundances_tmp_file_path
        )
    )

    pd.testing.assert_frame_equal(ld_0_abundances_df, lipidome_abundances.df)


def test_lipidome_abundances_get_subset(
    ld_0_abundances: LipidomeAbundances,
    ld_0_abundances_subset_df: pd.DataFrame,
    ld_0_abundances_index_subset: pd.Index,
    ld_0_abundances_column_subset: pd.Index,
) -> None:
    test_abundances_subset_df: pd.DataFrame = ld_0_abundances.get_subset(
        lipidomes=ld_0_abundances_index_subset,
        lipids=ld_0_abundances_column_subset,
    ).df

    pd.testing.assert_frame_equal(
        ld_0_abundances_subset_df, test_abundances_subset_df
    )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_abundances_get_aggregation_data_0",
        "ld_0_abundances_get_aggregation_data_1",
        "ld_0_abundances_get_aggregation_data_2",
    ],
)
def test_lipidome_abundances_gen_aggregations_by_lipidomes(
    aggregation_data_fixture_name: str,
    ld_0_abundances: LipidomeAbundances,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_test_data: AbundancesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    test_lipidome_abundances: LipidomeAbundances = (
        ld_0_abundances.gen_aggregations_by_lipidomes(
            aggregation_test_data.lipidome_indices,
            group_names=aggregation_test_data.group_names,
            operation=cast(
                Literal["mean", "std"], aggregation_test_data.operation
            ),
            nan_handling=aggregation_test_data.nan_handling,
        )
    )

    pd.testing.assert_frame_equal(
        aggregation_test_data.lipidome_abundances.df,
        test_lipidome_abundances.df,
    )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_abundances_add_aggregation_data_0",
        "ld_0_abundances_add_aggregation_data_1",
        "ld_0_abundances_add_aggregation_data_2",
    ],
)
def test_lipidome_abundances_add_aggregations_by_lipidomes(
    aggregation_data_fixture_name: str,
    ld_0_abundances: LipidomeAbundances,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_test_data: AbundancesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    test_lipidome_abundances: LipidomeAbundances = LipidomeAbundances(
        ld_0_abundances.df.copy(deep=True)
    )

    test_lipidome_abundances.add_aggregations_by_lipidomes_in_place(
        aggregation_test_data.lipidome_indices,
        group_names=aggregation_test_data.group_names,
        operation=cast(
            Literal["mean", "std"], aggregation_test_data.operation
        ),
        nan_handling=aggregation_test_data.nan_handling,
    )

    pd.testing.assert_frame_equal(
        aggregation_test_data.lipidome_abundances.df,
        test_lipidome_abundances.df,
    )
