"""Module concerning lipidome dataset unstacking."""

import logging

from typing import Literal

import pandas as pd

from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset

from lipidome_projector.lipidome.col_names import ColNames


logger: logging.Logger = logging.getLogger(__name__)

# TODO: Make part of DS wrapper.


def get_change_sample_unstacked_df(
    lipidome_ds: LipidomeDataset,
    abundance_change_type: Literal["difference", "fc", "log2fc"],
    from_lipidome: str,
    to_lipidome: str,
    col_names: ColNames,
) -> pd.DataFrame:
    lipidome_pair_change: pd.DataFrame = (
        lipidome_ds.abundance_change_storage.get_lipidome_pair_change(
            abundance_change_type,
            from_lipidome,
            to_lipidome,
        )
        .rename(col_names.change)
        .reset_index()
        .rename(columns={"index": col_names.lipid})
    )

    unstacked_change_df: pd.DataFrame = lipidome_pair_change.merge(
        lipidome_ds.lipid_features.df,
        left_on=col_names.lipid,
        right_index=True,
    ).dropna(subset=[col_names.change])

    return unstacked_change_df


def get_unstacked_dataset_df(
    lipidome_ds: LipidomeDataset,
    col_names: ColNames,
) -> pd.DataFrame:
    unstacked_abundances_df: pd.DataFrame = (
        lipidome_ds.abundance_df.unstack()
        .rename(col_names.abundance)  # type: ignore
        .to_frame()
        .reset_index()
        .rename(columns={"level_0": col_names.lipid})
    )

    unstacked_dataset_df: pd.DataFrame = (
        unstacked_abundances_df.merge(
            lipidome_ds.lipidome_features_df,
            how="left",
            left_on=col_names.lipidome,
            right_index=True,
            suffixes=("", "_DROP_DUPLICATE"),
        )
        .merge(
            lipidome_ds.lipid_features_df,
            how="left",
            left_on=col_names.lipid,
            right_index=True,
        )
        .dropna(subset=[col_names.abundance])
    )

    unstacked_dataset_df.drop(
        columns=[
            col
            for col in unstacked_dataset_df.columns
            if "_DROP_DUPLICATE" in col
        ],
        inplace=True,
    )

    return unstacked_dataset_df
