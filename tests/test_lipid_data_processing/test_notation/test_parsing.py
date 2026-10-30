"""Module concerning the testing of parsing."""

import logging

import pandas as pd

from lipid_data_processing.notation.parsing import (
    ParsedDataset,
    parse_name_series,
)


logger: logging.Logger = logging.getLogger(__name__)


def test_parser_wrapper_series_parsing(
    full_original_name_series: pd.Series,
    full_parsed_df: pd.DataFrame,
    parsing_relevant_col_names: list[str],
) -> None:
    parsed_dataset: ParsedDataset = parse_name_series(
        full_original_name_series
    )

    test_parsed_df: pd.DataFrame = parsed_dataset.df

    pd.testing.assert_frame_equal(
        full_parsed_df[parsing_relevant_col_names],
        test_parsed_df[parsing_relevant_col_names],
    )
