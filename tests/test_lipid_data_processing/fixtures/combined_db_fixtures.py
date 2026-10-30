"""Module concerning combined database fixtures."""

import logging

import pandas as pd
import pytest

from tests.test_lipid_data_processing.util.lipid_description import (
    LipidCollection,
)
from tests.test_lipid_data_processing.fixtures.lmsd_fixtures import *  # noqa: F401, F403, E501
from tests.test_lipid_data_processing.fixtures.sl_fixtures import *  # noqa: F401, F403, E501

logger: logging.Logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def combined_db_lipid_list(
    lmsd_lipids: LipidCollection,
    sl_lipids: LipidCollection,
) -> LipidCollection:
    return lmsd_lipids.concat([sl_lipids])


@pytest.fixture(scope="session")
def combined_db_original_names(
    lmsd_lipids: LipidCollection,
    sl_lipids: LipidCollection,
) -> pd.Series:
    return pd.concat(
        [
            lmsd_lipids.to_lmsd_original_name_series(),
            sl_lipids.to_sl_original_name_series(),
        ]
    )


@pytest.fixture(scope="session")
def combined_db_parsed_df(
    lmsd_lipids: LipidCollection,
    sl_lipids: LipidCollection,
) -> pd.DataFrame:
    return pd.concat(
        [
            lmsd_lipids.to_lmsd_generic_parsed_df(),
            sl_lipids.to_sl_parsed_df(),
        ]
    )
