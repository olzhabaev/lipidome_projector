"""Module concerning the (de)serialization of the lipidome datasets."""

import logging

from enum import StrEnum

import pandas as pd

from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset

from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.lipidome.col_names import ColNames


logger: logging.Logger = logging.getLogger(__name__)

# TODO: Utilize introduced abstractions, abstract further.


# TODO: Make a dataclass, pass as parameter.
class ColDefHeaders(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    abundance = "ABUNDANCE"
    features = "FEATURES"
    lipid = "LIPID"
    vectors = "VECTORS"
    change = "CHANGE"


def front_end_to_lipidome_ds(
    lipidome_fe_data: LipidomeFrontEndData,
    col_names: ColNames,
    use_virtual: bool = False,
) -> LipidomeDataset:
    """Create a lipidome dataset from the front end data.
    :param lipidome_fe_data: Lipidome front end data.
    :param use_virtual: Use virtual records.
    :returns: Lipidome dataset.
    """
    lipid_features_df: pd.DataFrame = _lipid_records_to_df(
        (
            lipidome_fe_data.lipid_records
            if not use_virtual
            else lipidome_fe_data.lipid_virtual_records
        ),
        col_names.lipid,
    )

    lipidome_df: pd.DataFrame = _lipidome_records_to_df(
        (
            lipidome_fe_data.lipidome_records
            if not use_virtual
            else lipidome_fe_data.lipidome_virtual_records
        ),
        col_names.lipidome,
    )

    abundance_df: pd.DataFrame = lipidome_df[lipid_features_df.index].astype(
        "float"
    )

    lipidome_features_df: pd.DataFrame = lipidome_df.drop(
        lipid_features_df.index, axis="columns"
    )

    differences_df: pd.DataFrame | None = _change_records_to_df(
        lipidome_fe_data.difference_records,
        lipidome_fe_data.difference_col_groups_defs,
        col_names.from_lipidome,
        col_names.to_lipidome,
    )

    log2fcs_df: pd.DataFrame | None = _change_records_to_df(
        lipidome_fe_data.log2fc_records,
        lipidome_fe_data.log2fc_col_groups_defs,
        col_names.from_lipidome,
        col_names.to_lipidome,
    )

    lipidome_ds: LipidomeDataset = LipidomeDataset.from_prepared_dfs(
        name=lipidome_fe_data.name,
        abundance_df=abundance_df,
        lipidome_features_df=lipidome_features_df,
        lipid_features_df=lipid_features_df,
        differences_df=differences_df,
        log2fcs_df=log2fcs_df,
    )

    return lipidome_ds


def _lipid_records_to_df(
    lipid_records: list[dict], lipid_col_name: str
) -> pd.DataFrame:
    lipid_features_df: pd.DataFrame = pd.DataFrame.from_records(
        lipid_records
    ).set_index(lipid_col_name)

    return lipid_features_df


def _lipidome_records_to_df(
    lipidome_records: list[dict], lipidome_col_name: str
) -> pd.DataFrame:
    lipidome_df: pd.DataFrame = pd.DataFrame.from_records(
        lipidome_records
    ).set_index(lipidome_col_name)

    return lipidome_df


def _change_records_to_df(
    change_records: list[dict],
    change_col_defs: list[dict],
    from_col_name: str,
    to_col_name: str,
) -> pd.DataFrame | None:
    if len(change_col_defs) == 0:
        return None

    field_definitions: list[dict] = next(
        column_group["children"]
        for column_group in change_col_defs
        if column_group["headerName"] == ColDefHeaders.change
    )

    columns: list[str] = [col_def["field"] for col_def in field_definitions]

    change_df: pd.DataFrame = (
        pd.DataFrame.from_records(
            change_records,
            columns=columns,
        )
        .set_index([from_col_name, to_col_name])
        .astype("float")
    )

    return change_df


def lipidome_ds_to_lipidome_fe_data(
    lipidome_ds: LipidomeDataset, col_names: ColNames
) -> LipidomeFrontEndData:
    """Create a lipidome front end data from a lipidome dataset.
    :param lipidome_ds: Lipidome dataset.
    :param col_names: Column names.
    :returns: Lipidome front end data.
    """
    lipidome_grid_col_groups_defs: list[dict] = _gen_lipidome_col_groups(
        lipidome_ds.abundance_df,
        lipidome_ds.lipidome_features_df,
        col_names.lipidome,
        col_names.color,
    )

    lipidome_grid_records: list[dict] = _gen_lipidome_records(
        lipidome_ds.lipidome_features_df,
        lipidome_ds.abundance_df,
        col_names.row_id,
    )

    lipid_grid_col_groups_defs: list[dict] = _gen_lipid_col_groups(
        lipidome_ds.lipid_features_df.index.name,
        col_names.vec_space_full,
        col_names.smiles,
        lipidome_ds.lipid_features_df,
    )

    lipid_grid_records: list[dict] = _gen_lipid_records(
        lipidome_ds.lipid_features_df
    )

    difference_grid_col_groups_defs: list[dict] = _gen_change_col_groups(
        lipidome_ds.get_change_df("difference")
    )

    difference_grid_records: list[dict] = _gen_change_records(
        lipidome_ds.get_change_df("difference")
    )

    log2fc_grid_col_groups_defs: list[dict] = _gen_change_col_groups(
        lipidome_ds.get_change_df("log2fc")
    )

    log2fc_grid_records: list[dict] = _gen_change_records(
        lipidome_ds.get_change_df("log2fc")
    )

    lipidome_ouput_scheme: LipidomeFrontEndData = LipidomeFrontEndData(
        name=lipidome_ds.name,
        lipidome_records=lipidome_grid_records,
        lipidome_col_groups_defs=lipidome_grid_col_groups_defs,
        lipid_records=lipid_grid_records,
        lipid_col_groups_defs=lipid_grid_col_groups_defs,
        difference_records=difference_grid_records,
        difference_col_groups_defs=difference_grid_col_groups_defs,
        log2fc_records=log2fc_grid_records,
        log2fc_col_groups_defs=log2fc_grid_col_groups_defs,
    )

    return lipidome_ouput_scheme


def _gen_lipidome_col_groups(
    lipidome_abundances_df: pd.DataFrame,
    lipidome_features_df: pd.DataFrame,
    lipidome_col_name: str,
    color_col_name: str,
) -> list[dict]:
    abundance_col_defs: list[dict] = _gen_abundnace_col_defs(
        lipidome_abundances_df, lipidome_col_name
    )

    lipidome_features_col_defs: list[dict] = _gen_lipidome_features_col_defs(
        lipidome_features_df, lipidome_col_name, color_col_name
    )

    lipidome_col_groups: list[dict] = [
        {
            "headerName": ColDefHeaders.features,
            "children": lipidome_features_col_defs,
            "openByDefault": True,
        },
        {
            "headerName": ColDefHeaders.abundance,
            "children": abundance_col_defs,
            "openByDefault": True,
        },
    ]

    return lipidome_col_groups


def _gen_abundnace_col_defs(
    lipidome_abundances_df: pd.DataFrame,
    lipidome_col_name: str,
) -> list[dict]:
    abundance_col_defs: list[dict] = [
        {
            "field": col,
            "filter": "agNumberColumnFilter",
            "floatingFilter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "sortable": True,
            "columnGroupShow": (
                "open" if col != lipidome_col_name else "closed"
            ),
            "valueFormatter": {
                "function": "params.value ? params.value.toExponential(2) : null;"  # noqa: E501
            },
        }
        for col in lipidome_abundances_df.reset_index().columns
    ]

    return abundance_col_defs


def _gen_lipidome_features_col_defs(
    lipidome_features_df: pd.DataFrame,
    lipidome_col_name: str,
    color_col_name: str,
) -> list[dict]:
    lipidome_col_def: dict = {
        "field": lipidome_col_name,
        "filter": True,
        "floatingFilter": True,
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "sortable": True,
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
        "headerCheckboxSelectionFilteredOnly": True,
    }

    color_col_def: dict = {
        "field": color_col_name,
        "filter": True,
        "floatingFilter": True,
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "sortable": True,
        "columnGroupShow": "open",
        "cellStyle": {
            "function": "params.value && {'backgroundColor': params.value}"
        },
    }

    feature_cols: list[str] = [
        col
        for col in lipidome_features_df.reset_index().columns
        if col != lipidome_col_name and col != color_col_name
    ]

    lipidome_features_col_defs: list[dict] = [
        {
            "field": col,
            "filter": True,
            "floatingFilter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "sortable": True,
            "columnGroupShow": "open",
        }
        for col in feature_cols
    ]

    combined_col_defs: list[dict] = [
        lipidome_col_def,
        color_col_def,
        *lipidome_features_col_defs,
    ]

    return combined_col_defs


def _gen_lipidome_records(
    lipidome_features_df: pd.DataFrame,
    lipidome_abundances_df: pd.DataFrame,
    row_id_col_name: str,
) -> list[dict]:
    lipidome_df: pd.DataFrame = pd.concat(
        [lipidome_features_df, lipidome_abundances_df],
        axis="columns",
        verify_integrity=True,
    )

    lipidome_df[row_id_col_name] = range(len(lipidome_df))

    lipidome_records: list[dict] = lipidome_df.reset_index().to_dict("records")

    return lipidome_records


def _gen_lipid_col_groups(
    lipid_col_name: str,
    vector_col_names: tuple[str, ...],
    smiles_col_name: str,
    lipid_features_df: pd.DataFrame,
) -> list[dict]:
    lipid_features_col_defs: list[dict] = [
        {
            "field": name,
            "filter": True,
            "floatingFilter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "sortable": True,
            "columnGroupShow": "open" if name != lipid_col_name else None,
        }
        for name in lipid_features_df.reset_index().columns
        if name not in vector_col_names and name != smiles_col_name
    ]

    lipid_vectors_col_defs: list[dict] = [
        {
            "field": name,
            "filter": "agNumberColumnFilter",
            "floatingFilter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "sortable": True,
            "columnGroupShow": "open" if name != vector_col_names[0] else None,
            "valueFormatter": {
                "function": "params.value ? params.value.toExponential(2) : null;"  # noqa: E501
            },
        }
        for name in vector_col_names
    ]

    lipid_col_groups: list[dict] = [
        {
            "headerName": ColDefHeaders.lipid,
            "children": lipid_features_col_defs,
            "openByDefault": True,
        },
        {
            "headerName": ColDefHeaders.vectors,
            "children": lipid_vectors_col_defs,
            "openByDefault": False,
        },
    ]

    return lipid_col_groups


def _gen_lipid_records(lipid_features_df: pd.DataFrame) -> list[dict]:
    lipid_records: list[dict] = lipid_features_df.reset_index().to_dict(
        "records"
    )

    return lipid_records


def _gen_change_records(change_df: pd.DataFrame) -> list[dict]:
    change_records: list[dict] = change_df.reset_index().to_dict("records")

    return change_records


def _gen_change_col_groups(
    change_df: pd.DataFrame,
) -> list[dict]:
    change_val_col_defs: list[dict] = [
        {
            "field": col,
            "filter": "agNumberColumnFilter",
            "floatingFilter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "sortable": True,
            "columnGroupShow": "open",
            "valueFormatter": {
                "function": "params.value ? params.value.toExponential(2) : null;"  # noqa: E501
            },
        }
        for col in change_df
    ]

    change_index_col_defs: list[dict] = [
        {
            "field": col,
            "filter": True,
            "floatingFilter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "sortable": True,
            "columnGroupShow": "open",
        }
        for col in change_df.index.names
    ]

    change_col_defs: list[dict] = change_index_col_defs + change_val_col_defs

    change_col_groups: list[dict] = [
        {
            "headerName": ColDefHeaders.change,
            "children": change_col_defs,
            "openByDefault": True,
        },
    ]

    return change_col_groups
