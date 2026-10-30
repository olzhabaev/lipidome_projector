"""Module concerning the testing of database IO."""

import logging

from pathlib import Path

import pandas as pd

from lipid_data_processing.databases.lmsd import LMSD
from lipid_data_processing.databases.swiss_lipids import SwissLipids
from tests.test_lipid_data_processing.util.lipid_description import (
    LMSDLipid,
    SLLipid,
)

logger: logging.Logger = logging.getLogger(__name__)


def test_lmsd_sdf_to_df(
    lmsd_tmp_file_path: Path, lmsd_df: pd.DataFrame
) -> None:
    test_lmsd: LMSD = LMSD.from_source_file(
        lmsd_tmp_file_path, add_rdkit_data=False
    )

    test_lmsd_df: pd.DataFrame = test_lmsd.df

    pd.testing.assert_index_equal(lmsd_df.index, test_lmsd_df.index)

    pd.testing.assert_frame_equal(
        lmsd_df.reset_index(),
        test_lmsd_df.reset_index()[LMSDLipid.col_name_map.values()],
    )


def test_sl_tsv_to_df(sl_tmp_file_path: Path, sl_df: pd.DataFrame) -> None:
    test_sl: SwissLipids = SwissLipids.from_source_file(
        sl_tmp_file_path, add_rdkit_data=False, drop_non_isomers=False
    )

    test_sl_df: pd.DataFrame = test_sl.df

    pd.testing.assert_index_equal(sl_df.index, test_sl_df.index)

    pd.testing.assert_frame_equal(
        sl_df.reset_index(),
        test_sl_df.reset_index()[SLLipid.col_name_map.values()],
    )
