"""Module concerning the matching of lipid datasets."""

import logging

import pandas as pd

from tests.test_lipid_data_processing.util.matching_description import (
    MatchingCase,
)

logger: logging.Logger = logging.getLogger(__name__)


def test_perform_constrained_match_matches(
    matching_case_1: MatchingCase,
) -> None:
    pd.testing.assert_frame_equal(
        matching_case_1.target_matching_results.matches_info.dataframe,
        matching_case_1.test_matching_results.matches_info.dataframe,
    )


def test_perform_constrained_match_constrained_matches(
    matching_case_1: MatchingCase,
) -> None:
    pd.testing.assert_frame_equal(
        matching_case_1.target_matching_results.constrained_matches_info.dataframe,  # noqa: E501
        matching_case_1.test_matching_results.constrained_matches_info.dataframe,  # noqa: E501
    )


def test_perform_constrained_match_parsed_no_match(
    matching_case_1: MatchingCase,
) -> None:
    pd.testing.assert_frame_equal(
        matching_case_1.target_matching_results.parsed_no_match.dataframe,
        matching_case_1.test_matching_results.parsed_no_match.dataframe,
    )


def test_perform_constrained_match_original_name_no_match(
    matching_case_1: MatchingCase,
) -> None:
    pd.testing.assert_frame_equal(
        matching_case_1.target_matching_results.original_name_no_match.dataframe,  # noqa: E501
        matching_case_1.test_matching_results.original_name_no_match.dataframe,
    )


def test_perform_constrained_match_filtered_lipids(
    matching_case_1: MatchingCase,
) -> None:
    pd.testing.assert_frame_equal(
        matching_case_1.target_matching_results.filtered_lipids.dataframe,
        matching_case_1.test_matching_results.filtered_lipids.dataframe,
        check_dtype=False,
    )
