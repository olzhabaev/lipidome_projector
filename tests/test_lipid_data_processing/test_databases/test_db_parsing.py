"""Module concerning the testing of database parsing."""

import logging

import pandas as pd
import pytest

from lipid_data_processing.databases.lmsd import LMSD
from lipid_data_processing.databases.swiss_lipids import SwissLipids


logger: logging.Logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "fsp,lmsd_parsed_df_fixture_name",
    [(False, "lmsd_generic_parsed_df"), (True, "lmsd_sp_parsed_df")],
)
def test_parse_lmsd(
    fsp: bool,
    lmsd_parsed_df_fixture_name: str,
    lmsd: LMSD,
    request,
) -> None:
    parsed_df: pd.DataFrame = lmsd.parse(
        add_failures_parsed_species=fsp, add_categories_to_unparsed=fsp
    ).df

    test_parsed_df: pd.DataFrame = parsed_df.drop(
        columns=["STATUS", "MESSAGE"]
    )

    target_parsed_df: pd.DataFrame = request.getfixturevalue(
        lmsd_parsed_df_fixture_name
    ).drop(columns=["STATUS", "MESSAGE"])

    pd.testing.assert_frame_equal(target_parsed_df, test_parsed_df)


def test_parse_sl(
    swiss_lipids: SwissLipids, sl_parsed_df: pd.DataFrame
) -> None:
    parsed_df: pd.DataFrame = swiss_lipids.parse().df

    test_parsed_df: pd.DataFrame = parsed_df.drop(
        columns=["STATUS", "MESSAGE"]
    )

    target_parsed_df: pd.DataFrame = sl_parsed_df.drop(
        columns=["STATUS", "MESSAGE"]
    )

    pd.testing.assert_frame_equal(target_parsed_df, test_parsed_df)
