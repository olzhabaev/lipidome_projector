"""Module concerning the unified LMSD / SL database class."""

import logging

from typing import Literal, Self

import pandas as pd

from lipid_data_processing.databases.base_db_classes import (
    UnifiedDatabase,
    UnifiedDBColNames,
)
from lipid_data_processing.databases.lmsd import UnifiedLMSD
from lipid_data_processing.databases.swiss_lipids import UnifiedSL
from lipid_data_processing.notation.parsing import ParsedDataset


logger: logging.Logger = logging.getLogger(__name__)


class UnifiedLMSDSL(UnifiedDatabase):
    @classmethod
    def from_source_data(
        cls,
        lmsd_df: pd.DataFrame,
        lmsd_parsed_ds: ParsedDataset,
        sl_df: pd.DataFrame,
        sl_parsed_ds: ParsedDataset,
        keep_overlap_from: Literal["lmsd", "sl", "both"],
        col_names: UnifiedDBColNames | None = None,
    ) -> Self:
        unified_lmsd: UnifiedLMSD = UnifiedLMSD.from_source_data(
            lmsd_df, lmsd_parsed_ds, col_names
        )
        unified_sl: UnifiedSL = UnifiedSL.from_source_data(
            sl_df, sl_parsed_ds, col_names
        )
        if keep_overlap_from != "both":
            unified_lmsd, unified_sl = cls._remove_lmsd_sl_ud_overlap(
                unified_lmsd,
                lmsd_df,
                unified_sl,
                sl_df,
                keep_overlap_from,
            )

        unified_lmsd_sl: UnifiedDatabase = unified_lmsd.concat([unified_sl])

        return cls(unified_lmsd_sl.df)

    @staticmethod
    def _remove_lmsd_sl_ud_overlap(
        lmsd_ud: UnifiedLMSD,
        lmsd_df: pd.DataFrame,
        sl_ud: UnifiedSL,
        sl_df: pd.DataFrame,
        keep_overlap_from: Literal["lmsd", "sl"],
    ) -> tuple[UnifiedLMSD, UnifiedSL]:
        lmsd_sl_overlap: pd.Series = (
            sl_df[sl_df["LIPID MAPS"].isin(lmsd_df.index)]["LIPID MAPS"]
            .dropna()
            .drop_duplicates()
        )

        if keep_overlap_from == "lmsd":
            sl_subset_index: pd.Index = sl_ud.df.index.difference(
                lmsd_sl_overlap.index
            )
            sl_subset_index.name = sl_ud.df.index.name
            sl_ud = UnifiedSL(sl_ud.df.loc[sl_subset_index])
        elif keep_overlap_from == "sl":
            lmsd_subset_index: pd.Index = lmsd_ud.df.index.difference(
                pd.Index(lmsd_sl_overlap.values)
            )
            lmsd_subset_index.name = lmsd_ud.df.index.name
            lmsd_ud = UnifiedLMSD(lmsd_ud.df.loc[lmsd_subset_index])
        else:
            raise ValueError("Incorrect specification of overlap source.")

        return lmsd_ud, sl_ud
