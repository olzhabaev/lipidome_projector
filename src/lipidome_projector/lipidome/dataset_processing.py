"""Module concerning the processing of abundnace changes."""

import logging

import pandas as pd

from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.lipidome.grid_processing import (
    gen_ds_and_filters,
)
from lipidome_projector.lipidome.translation import (
    lipidome_ds_to_lipidome_fe_data,
)


logger: logging.Logger = logging.getLogger(__name__)

# TODO Extract to lipidome ds wrapper / abstraction.


def add_grouping(
    aggregation_type: str,
    grouping_name: str,
    lipidome_fe_data_input: LipidomeFrontEndData,
    col_names: ColNames,
) -> LipidomeFrontEndData:
    """Add grouping to the lipidome dataset.
    :param aggregation_type: Aggregation type.
    :param lipidome_fe_data_input: Lipidome front end data.
    :param col_names: Column names.
    :return: Lipidome front end data.
    """
    lipidome_ds, lipidome_filter, _ = gen_ds_and_filters(
        lipidome_fe_data_input, col_names, "selected"
    )

    lipidome_ds.add_aggregations_by_lipidomes_in_place(
        lipidomes_list=[lipidome_filter],
        operation=aggregation_type,  # type: ignore
        group_names=[grouping_name],
    )

    new_colors: pd.Series = _overwrite_concat_colors(
        lipidome_ds.lipidome_features_df[col_names.color]
    )

    lipidome_ds.add_feature_in_place(
        name=col_names.color,
        values=new_colors,
        overwrite=True,
        validate=True,
    )

    lipidome_fe_data_output: LipidomeFrontEndData = (
        lipidome_ds_to_lipidome_fe_data(
            lipidome_ds=lipidome_ds, col_names=col_names
        )
    )

    return lipidome_fe_data_output


def _overwrite_concat_colors(colors: pd.Series) -> pd.Series:
    new_colors: pd.Series = colors.apply(
        lambda color: color if _is_simple_hex_color(color) else "#000000"
    )

    return new_colors


def _is_simple_hex_color(color: str) -> bool:
    return len(color) == 7 and color.startswith("#")


def add_pairwise_changes(
    change_type: str,
    lipidome_fe_data_input: LipidomeFrontEndData,
    col_names: ColNames,
) -> LipidomeFrontEndData:
    """Add pairwise changes to the lipidome dataset.
    :return: Lipidome front end data.
    """
    lipidome_ds, lipidome_filter, _ = gen_ds_and_filters(
        lipidome_fe_data_input, col_names, "selected"
    )

    lipidome_ds.add_pairwise_changes_in_place(
        change_type,  # type: ignore
        lipidomes=lipidome_filter,
        exists_handling="overwrite",
    )

    lipidome_fe_data_output: LipidomeFrontEndData = (
        lipidome_ds_to_lipidome_fe_data(
            lipidome_ds=lipidome_ds, col_names=col_names
        )
    )

    return lipidome_fe_data_output
