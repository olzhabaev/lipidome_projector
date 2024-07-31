"""Module concerning the post-processing of lipidome datasets."""

import logging

import pandas as pd

from embedding_visualization.colors import generate_discrete_hex_colormap

from lipidome_projector.lipidome.col_names import ColNames
from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset


logger: logging.Logger = logging.getLogger(__name__)


# TODO: Extract to universal lipidome DS creation (upload / default).
def process_lipidome_ds(
    lipidome_ds: LipidomeDataset, col_names: ColNames
) -> None:
    """Process the lipidome dataset.
    :param lipidome_ds: Lipidome dataset.
    :param col_names: Column names.
    """
    _adjust_index_names(lipidome_ds, col_names)
    _add_color_feature(lipidome_ds, col_names.color)


# TODO: Extract, this is the lipidome datasets concern on creation.
def _adjust_index_names(
    lipidome_ds: LipidomeDataset, col_names: ColNames
) -> None:
    lipidome_ds.abundance_df.index.rename(col_names.lipidome, inplace=True)

    lipidome_ds.lipidome_features_df.index.rename(
        col_names.lipidome, inplace=True
    )

    lipidome_ds.lipid_features_df.index.rename(col_names.lipid, inplace=True)

    lipidome_ds.abundance_change_storage.differences.df.index.rename(
        (col_names.from_lipidome, col_names.to_lipidome), inplace=True
    )

    lipidome_ds.abundance_change_storage.fcs.df.index.rename(
        (col_names.from_lipidome, col_names.to_lipidome), inplace=True
    )

    lipidome_ds.abundance_change_storage.log2fcs.df.index.rename(
        (col_names.from_lipidome, col_names.to_lipidome), inplace=True
    )


def _add_color_feature(lipidome_ds: LipidomeDataset, col_name: str) -> None:
    colors: pd.Series = pd.Series(
        generate_discrete_hex_colormap(lipidome_ds.lipidomes.to_list(), "T10")
    )

    lipidome_ds.add_feature_in_place(
        col_name, colors, overwrite=True, validate=True
    )
