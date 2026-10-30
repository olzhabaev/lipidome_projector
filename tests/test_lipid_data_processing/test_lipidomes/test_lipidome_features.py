"""Module concerning the testing of lipidome features."""

import logging

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from lipid_data_processing.lipidomes.lipidome_features import LipidomeFeatures
from tests.test_lipid_data_processing.util.lipidome_description import (
    LipidomeFeaturesAggregationTestData,
    LipidomeFeaturesAddFeatureTestData,
)

logger: logging.Logger = logging.getLogger(__name__)


def test_lipidome_features_creation_success(
    ld_0_lipidome_features_df: pd.DataFrame,
) -> None:
    lipidome_features: LipidomeFeatures = LipidomeFeatures(
        ld_0_lipidome_features_df
    )

    pd.testing.assert_frame_equal(
        lipidome_features.df, ld_0_lipidome_features_df
    )


def test_lipidome_features_creation_failure_duplicated_index(
    ld_0_lipidome_features_df: pd.DataFrame,
) -> None:
    duplicated_df: pd.DataFrame = pd.concat(
        [ld_0_lipidome_features_df, ld_0_lipidome_features_df], axis="index"
    )
    with pytest.raises(ValueError, match="duplicated indices"):
        LipidomeFeatures(duplicated_df)


def test_lipidome_features_creation_failure_duplicated_columns(
    ld_0_lipidome_features_df: pd.DataFrame,
) -> None:
    duplicated_columns_df: pd.DataFrame = pd.concat(
        [ld_0_lipidome_features_df, ld_0_lipidome_features_df], axis="columns"
    )
    with pytest.raises(ValueError, match="duplicated columns"):
        LipidomeFeatures(duplicated_columns_df)


def test_lipidome_features_creation_from_str_io(
    ld_0_lipidome_features_df: pd.DataFrame,
    ld_0_lipidome_features_str_io: StringIO,
) -> None:
    lipidome_features: LipidomeFeatures = LipidomeFeatures.from_csv_input(
        ld_0_lipidome_features_str_io
    )

    pd.testing.assert_frame_equal(
        ld_0_lipidome_features_df, lipidome_features.df
    )


def test_lipidome_features_creation_from_path(
    ld_0_lipidome_features_df: pd.DataFrame,
    ld_0_lipidome_features_tmp_file_path: Path,
) -> None:
    lipidome_features: LipidomeFeatures = LipidomeFeatures.from_csv_input(
        ld_0_lipidome_features_tmp_file_path
    )

    pd.testing.assert_frame_equal(
        ld_0_lipidome_features_df, lipidome_features.df
    )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_get_aggregation_data_0",
    ],
)
def test_lipidome_features_gen_aggregations_by_lipidomes(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    lipidome_features_aggregated: LipidomeFeatures = (
        ld_0_lipidome_features.gen_aggregations_by_lipidomes(
            lipidomes_list=aggregation_data.lipidome_indeces,
            group_names=aggregation_data.group_names,
        )
    )

    pd.testing.assert_frame_equal(
        aggregation_data.lipidome_features.df,
        lipidome_features_aggregated.df,
    )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_add_subset_aggregation_data_0",
    ],
)
def test_lipidome_features_add_aggregations(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
        lipidomes_list=aggregation_data.lipidome_indeces,
        group_names=aggregation_data.group_names,
    )

    pd.testing.assert_frame_equal(
        aggregation_data.lipidome_features.df,
        ld_0_lipidome_features.df,
    )


def test_lipidome_features_add_aggregations_empty_failure(
    ld_0_lipidome_features: LipidomeFeatures,
) -> None:
    with pytest.raises(ValueError, match="empty"):
        ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list=[],
            group_names=[],
        )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_add_subset_aggregation_data_0",
    ],
)
def test_lipidome_features_add_aggregations_less_than_two_failure(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    with pytest.raises(ValueError, match="at least 2"):
        ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list=[pd.Index([0])]
            * len(aggregation_data.lipidome_indeces),
            group_names=aggregation_data.group_names,
        )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_add_subset_aggregation_data_0",
    ],
)
def test_lipidome_features_add_aggregations_missing_indices_failure(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    changed_index_as_list: list = aggregation_data.lipidome_indeces[
        0
    ].to_list()
    changed_index_as_list[0] = "CHANGED"
    new_lipidome_indeces: list[pd.Index] = [
        pd.Index(changed_index_as_list),
    ] + aggregation_data.lipidome_indeces[1:]

    with pytest.raises(ValueError, match="CHANGED"):
        ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list=new_lipidome_indeces,
            group_names=aggregation_data.group_names,
        )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_add_subset_aggregation_data_0",
    ],
)
def test_lipidome_features_add_aggregations_num_group_names_failure(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    with pytest.raises(ValueError, match="Number of group names"):
        ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list=aggregation_data.lipidome_indeces,
            group_names=aggregation_data.group_names[:-1],
        )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_add_subset_aggregation_data_0",
    ],
)
def test_lipidome_features_add_aggregations_duplicate_group_names_failure(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    with pytest.raises(ValueError, match="duplicates"):
        ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list=aggregation_data.lipidome_indeces,
            group_names=aggregation_data.group_names[0:-1]
            + [
                aggregation_data.group_names[0],
            ],
        )


@pytest.mark.parametrize(
    "aggregation_data_fixture_name",
    [
        "ld_0_lipidome_features_add_subset_aggregation_data_0",
    ],
)
def test_lipidome_features_add_aggregations_present_group_names_failure(
    aggregation_data_fixture_name: str,
    ld_0_lipidome_features: LipidomeFeatures,
    request: pytest.FixtureRequest,
) -> None:
    aggregation_data: LipidomeFeaturesAggregationTestData = (
        request.getfixturevalue(aggregation_data_fixture_name)
    )

    changed_group_names: list[
        str
    ] = aggregation_data.lipidome_features.df.index.to_list()[
        : len(aggregation_data.group_names)
    ]

    with pytest.raises(ValueError, match="present"):
        ld_0_lipidome_features.add_aggregations_by_lipidomes_in_place(
            lipidomes_list=aggregation_data.lipidome_indeces,
            group_names=changed_group_names,
        )


def test_lipidome_features_add_feature(
    ld_0_lipidome_features_add_feature_data_0: LipidomeFeaturesAddFeatureTestData,  # noqa: E501
) -> None:
    target_original_features: LipidomeFeatures = (
        ld_0_lipidome_features_add_feature_data_0.lipidome_features
    )

    target_updated_features: LipidomeFeatures = (
        ld_0_lipidome_features_add_feature_data_0.updated_lipidome_features
    )

    test_updated_features: LipidomeFeatures = (
        target_original_features.add_feature(
            name=ld_0_lipidome_features_add_feature_data_0.feature_name,
            values=ld_0_lipidome_features_add_feature_data_0.feature_values,
            overwrite=False,
        )
    )

    pd.testing.assert_frame_equal(
        target_updated_features.df,
        test_updated_features.df,
    )


def test_lipidome_features_add_feature_in_place(
    ld_0_lipidome_features_add_feature_data_0: LipidomeFeaturesAddFeatureTestData,  # noqa: E501
) -> None:
    target_original_features: LipidomeFeatures = (
        ld_0_lipidome_features_add_feature_data_0.lipidome_features
    )

    target_updated_features: LipidomeFeatures = (
        ld_0_lipidome_features_add_feature_data_0.updated_lipidome_features
    )

    test_updated_features: LipidomeFeatures = LipidomeFeatures(
        target_original_features.df.copy()
    )
    test_updated_features.add_feature_in_place(
        name=ld_0_lipidome_features_add_feature_data_0.feature_name,
        values=ld_0_lipidome_features_add_feature_data_0.feature_values,
        overwrite=False,
    )

    pd.testing.assert_frame_equal(
        target_updated_features.df,
        test_updated_features.df,
    )


def test_lipidome_features_add_feature_exists_failure(
    ld_0_lipidome_features_add_feature_data_0: LipidomeFeaturesAddFeatureTestData,  # noqa: E501
) -> None:
    target_original_features: LipidomeFeatures = (
        ld_0_lipidome_features_add_feature_data_0.lipidome_features
    )

    existing_feature_name: str = (
        ld_0_lipidome_features_add_feature_data_0.lipidome_features.features[0]
    )

    with pytest.raises(ValueError, match="already exists"):
        target_original_features.add_feature(
            name=existing_feature_name,
            values=ld_0_lipidome_features_add_feature_data_0.feature_values,
            overwrite=False,
        )


def test_lipidome_features_add_feature_index_mismatch_failure(
    ld_0_lipidome_features_add_feature_data_0: LipidomeFeaturesAddFeatureTestData,  # noqa: E501
) -> None:
    target_original_features: LipidomeFeatures = (
        ld_0_lipidome_features_add_feature_data_0.lipidome_features
    )

    mismatched_values: pd.Series = (
        ld_0_lipidome_features_add_feature_data_0.feature_values.copy()
    )
    mismatched_values.index = mismatched_values.index.map(lambda x: x * 2)

    with pytest.raises(ValueError, match="Index of values does not match"):
        target_original_features.add_feature(
            name=ld_0_lipidome_features_add_feature_data_0.feature_name,
            values=mismatched_values,
            overwrite=False,
        )
