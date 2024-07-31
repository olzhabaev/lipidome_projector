"""Module concerning the processing of grid data callbacks."""

import logging

from typing import Literal

import pandas as pd

from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.lipidome.translation import (
    ColDefHeaders,
    front_end_to_lipidome_ds,
)
from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset


logger: logging.Logger = logging.getLogger(__name__)

# TODO Extract to grid / DS abstraction.


def gen_lipidome_lipid_filtered_state(
    lipidome_fe_data: LipidomeFrontEndData,
    col_names: ColNames,
    lipidome_filter_source: Literal["virtual", "selected"],
) -> tuple[list[dict], list[dict]]:
    """Generate the lipidome grid column state update based on the
    lipid grid filter.
    :param lipidome_fe_data: Lipidome front end data.
    :returns: Lipidome grid column state update.
    """
    lipid_filter: pd.Index
    _, lipid_filter = _gen_filters(
        lipidome_fe_data,
        col_names.lipidome,
        col_names.lipid,
        lipidome_filter_source,
    )

    feature_group: dict = next(
        column_group["children"]
        for column_group in lipidome_fe_data.lipidome_col_groups_defs
        if column_group["headerName"] == ColDefHeaders.features
    )

    abundance_group: dict = next(
        column_group["children"]
        for column_group in lipidome_fe_data.lipidome_col_groups_defs
        if column_group["headerName"] == ColDefHeaders.abundance
    )

    lipidome_features_col_state_update: list[dict] = [
        {"colId": column_def["field"], "hide": False}
        for column_def in feature_group
    ]

    from_to_col_state_update: list[dict] = [
        {
            "colId": col_names.from_lipidome,
            "hide": False,
        },
        {
            "colId": col_names.to_lipidome,
            "hide": False,
        },
    ]

    abundance_col_state_update: list[dict] = [
        {
            "colId": column_def["field"],
            "hide": (
                column_def["field"] not in lipid_filter
                and column_def["field"] != col_names.lipidome
            ),
        }
        for column_def in abundance_group
    ]

    lipidome_grid_col_state_update: list[dict] = (
        lipidome_features_col_state_update + abundance_col_state_update
    )

    change_grid_col_state_update: list[dict] = (
        from_to_col_state_update + abundance_col_state_update
    )

    return lipidome_grid_col_state_update, change_grid_col_state_update


def gen_ds_and_filters(
    lipidome_fe_data: LipidomeFrontEndData,
    col_names: ColNames,
    lipidome_filter_source: Literal["virtual", "selected"],
) -> tuple[LipidomeDataset, pd.Index, pd.Index]:
    """Generate the lipidome dataset and the lipid / lipidome filters
    from grid data.
    :param lipidome_fe_data: Lipidome front end data.
    :param col_names: Column names.
    :returns: Lipidome dataset and filters.
    """
    lipidome_ds: LipidomeDataset = front_end_to_lipidome_ds(
        lipidome_fe_data, col_names
    )

    lipidome_filter: pd.Index
    lipid_filter: pd.Index
    lipidome_filter, lipid_filter = _gen_filters(
        lipidome_fe_data,
        col_names.lipidome,
        col_names.lipid,
        lipidome_filter_source,
    )

    return lipidome_ds, lipidome_filter, lipid_filter


def _gen_filters(
    lipidome_fe_data: LipidomeFrontEndData,
    lipidome_col_name: str,
    lipid_col_name: str,
    lipidome_filter_source: Literal["virtual", "selected"],
) -> tuple[pd.Index, pd.Index]:
    if lipidome_filter_source == "virtual":
        filter_records: list[dict] = lipidome_fe_data.lipidome_virtual_records
    elif lipidome_filter_source == "selected":
        filter_records = lipidome_fe_data.lipidome_selected_records
    else:
        raise ValueError(
            f"Invalid lipidome filter source: {lipidome_filter_source}"
        )

    lipidome_filter: pd.Index = pd.Index(
        [record[lipidome_col_name] for record in filter_records]
    )

    lipid_filter: pd.Index = pd.Index(
        record[lipid_col_name]
        for record in lipidome_fe_data.lipid_virtual_records
    )

    return lipidome_filter, lipid_filter
