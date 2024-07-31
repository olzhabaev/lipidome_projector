"""Module concerning callbacks."""

import logging

from dash import callback, Input, no_update, Output, State
from dash._callback import NoUpdate

from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.upload_processing import (
    process_lipidome_upload,
    LipidomeUploadOutput,
)


logger: logging.Logger = logging.getLogger(__name__)


def reg_upload_callbacks_python(
    fe: FrontEnd, database: BaseDB, col_names: ColNames
) -> None:
    logger.info("Register upload python callbacks.")

    @callback(
        Output(fe.upload_modal.element_id, "is_open"),
        Input(fe.upload_setup_button.element_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_upload_modal(n_clicks: int) -> bool:
        return True

    @callback(
        Output(fe.upload_abundances.element_id, "children"),
        Input(fe.upload_abundances.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_abundance_upload(filename: str) -> str:
        return filename

    @callback(
        Output(fe.upload_lipidome_features.element_id, "children"),
        Input(fe.upload_lipidome_features.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_lipidome_features_upload(filename: str) -> str:
        return filename

    @callback(
        Output(fe.upload_fa_constraints.element_id, "children"),
        Input(fe.upload_fa_constraints.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_fa_constraints_upload(filename: str) -> str:
        return filename

    @callback(
        Output(fe.upload_lcb_constraints.element_id, "children"),
        Input(fe.upload_lcb_constraints.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_lcb_constraints_upload(filename: str) -> str:
        return filename

    @callback(
        Output(fe.upload_initiate_button.element_id, "disabled"),
        Input(fe.upload_abundances.element_id, "filename"),
        Input(fe.upload_lipidome_features.element_id, "filename"),
        Input(fe.upload_fa_constraints.element_id, "filename"),
        Input(fe.upload_lcb_constraints.element_id, "filename"),
        prevent_initial_call=True,
    )
    def enable_upload_initiate_button(
        filename_abundances: str,
        filename_lipidome_features: str,
        filename_fa_constraints: str,
        filename_lcb_constraints: str,
    ) -> bool:
        if (
            filename_abundances
            and filename_lipidome_features
            and filename_fa_constraints
            and filename_lcb_constraints
        ):
            return False

        return True

    @callback(
        Output(fe.lipidome_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.lipidome_grid.element_id, "virtualRowData", allow_duplicate=True
        ),
        Output(
            fe.lipidome_grid.element_id, "columnDefs", allow_duplicate=True
        ),
        Output(fe.lipid_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.lipid_grid.element_id, "virtualRowData", allow_duplicate=True
        ),
        Output(fe.lipid_grid.element_id, "columnDefs", allow_duplicate=True),
        Output(fe.difference_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.difference_grid.element_id,
            "virtualRowData",
            allow_duplicate=True,
        ),
        Output(
            fe.difference_grid.element_id, "columnDefs", allow_duplicate=True
        ),
        Output(fe.log2fc_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.log2fc_grid.element_id, "virtualRowData", allow_duplicate=True
        ),
        Output(fe.log2fc_grid.element_id, "columnDefs", allow_duplicate=True),
        Output(
            fe.upload_modal.footer_text_element_id,
            "children",
            allow_duplicate=True,
        ),
        Output(
            fe.upload_failures_grid.element_id,
            "columnDefs",
            allow_duplicate=True,
        ),
        Output(
            fe.upload_failures_grid.element_id, "rowData", allow_duplicate=True
        ),
        Output(
            fe.upload_failures_grid.element_id,
            "virtualRowData",
            allow_duplicate=True,
        ),
        Input(fe.upload_initiate_button.element_id, "n_clicks"),
        State(fe.upload_abundances.element_id, "filename"),
        State(fe.upload_abundances.element_id, "contents"),
        State(fe.upload_lipidome_features.element_id, "contents"),
        State(fe.upload_fa_constraints.element_id, "contents"),
        State(fe.upload_lcb_constraints.element_id, "contents"),
        prevent_initial_call=True,
    )
    def process_lipidome_upload_callback(
        n_clicks: int,
        abundances_filename: str,
        abundances_contents: str,
        lipidome_features_contents: str,
        fa_constraints_contents: str,
        lcb_constraints_contents: str,
    ) -> (
        tuple[
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            str,
            list[dict],
            list[dict],
            list[dict],
        ]
        | tuple[
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            NoUpdate,
            str,
            list,
            list,
            list,
        ]
    ):
        lipidome_output: LipidomeUploadOutput = process_lipidome_upload(
            name=abundances_filename,
            abundances_contents=abundances_contents,
            lipidome_features_contents=lipidome_features_contents,
            fa_constraints_contents=fa_constraints_contents,
            lcb_constraints_contents=lcb_constraints_contents,
            database=database,
            col_names=col_names,
        )

        if not lipidome_output.processing_failure:
            return (
                lipidome_output.lipidome_fe_data.lipidome_records,
                lipidome_output.lipidome_fe_data.lipidome_records,
                lipidome_output.lipidome_fe_data.lipidome_col_groups_defs,
                lipidome_output.lipidome_fe_data.lipid_records,
                lipidome_output.lipidome_fe_data.lipid_records,
                lipidome_output.lipidome_fe_data.lipid_col_groups_defs,
                lipidome_output.lipidome_fe_data.difference_records,
                lipidome_output.lipidome_fe_data.difference_records,
                lipidome_output.lipidome_fe_data.difference_col_groups_defs,
                lipidome_output.lipidome_fe_data.log2fc_records,
                lipidome_output.lipidome_fe_data.log2fc_records,
                lipidome_output.lipidome_fe_data.log2fc_col_groups_defs,
                fe.upload_modal.upload_success_text,
                lipidome_output.failures_column_defs,
                lipidome_output.failures_records,
                lipidome_output.failures_records,
            )
        else:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                fe.upload_modal.upload_failure_text,
                [],
                [],
                [],
            )
