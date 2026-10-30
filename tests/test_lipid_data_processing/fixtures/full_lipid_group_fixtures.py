"""Module concerning lipid group fixtures."""

import logging

import pandas as pd
import pytest


from tests.test_lipid_data_processing.fixtures.combined_db_fixtures import *  # noqa: F401, F403, E501
from tests.test_lipid_data_processing.fixtures.high_level_lipid_fixtures import *  # noqa: F401, F403, E501

logger: logging.Logger = logging.getLogger(__name__)


# * PARSED COLUNM NAMES -------------------------------------------------------


# * LIPID GROUPS --------------------------------------------------------------


@pytest.fixture(scope="session")
def full_original_name_series(
    combined_db_original_names: pd.Series,
    all_high_level_original_names: pd.Series,
) -> pd.Series:
    return pd.concat(
        [
            combined_db_original_names,
            all_high_level_original_names,
        ]
    )


@pytest.fixture(scope="session")
def full_parsed_df(
    combined_db_parsed_df: pd.DataFrame,
    all_high_level_parsed_df: pd.DataFrame,
) -> pd.DataFrame:
    return pd.concat(
        [
            combined_db_parsed_df,
            all_high_level_parsed_df,
        ]
    )
