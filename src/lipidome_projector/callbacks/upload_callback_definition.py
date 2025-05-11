"""Module concerning callbacks."""

import base64
import logging

from typing import Literal

from dash import callback, Input, no_update, Output, State
from dash._callback import NoUpdate
from dash.exceptions import PreventUpdate

from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.graph.scatter_cfg import ScatterCfg
from lipidome_projector.lipidome.grid_data import GridDataCollection
from lipidome_projector.lipidome.session import SessionState
from lipidome_projector.lipidome.upload_processing import (
    process_lipidome_upload,
    LipidomeUploadResults,
    LipidomeUploadFailure,
)


logger: logging.Logger = logging.getLogger(__name__)


def reg_upload_callbacks_python(
    fe: FrontEnd, database: BaseDB, col_names: ColNames
) -> None:
    logger.info("Register upload python callbacks.")

    @callback(
        Output(fe.upload_modal.element_id, "is_open", allow_duplicate=True),
        Input(fe.upload_setup_button.element_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_upload_modal(n_clicks: int) -> bool:
        return True

    @callback(
        Output(
            fe.upload_abundances.element_id, "children", allow_duplicate=True
        ),
        Input(fe.upload_abundances.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_abundance_upload(filename: str) -> str:
        return filename

    @callback(
        Output(
            fe.upload_lipidome_features.element_id,
            "children",
            allow_duplicate=True,
        ),
        Input(fe.upload_lipidome_features.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_lipidome_features_upload(filename: str) -> str:
        return filename

    @callback(
        Output(
            fe.upload_fa_constraints.element_id,
            "children",
            allow_duplicate=True,
        ),
        Input(fe.upload_fa_constraints.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_fa_constraints_upload(filename: str) -> str:
        return filename

    @callback(
        Output(
            fe.upload_lcb_constraints.element_id,
            "children",
            allow_duplicate=True,
        ),
        Input(fe.upload_lcb_constraints.element_id, "filename"),
        prevent_initial_call=True,
    )
    def register_lcb_constraints_upload(filename: str) -> str:
        return filename

    @callback(
        Output(
            fe.upload_initiate_button.element_id,
            "disabled",
            allow_duplicate=True,
        ),
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
        lipidome_output: LipidomeUploadResults | LipidomeUploadFailure = (
            process_lipidome_upload(
                name=abundances_filename,
                abundances_contents=abundances_contents,
                lipidome_features_contents=lipidome_features_contents,
                fa_constraints_contents=fa_constraints_contents,
                lcb_constraints_contents=lcb_constraints_contents,
                database=database,
                col_names=col_names,
            )
        )

        return lipidome_output.get_callback_output()

    @callback(
        Output(fe.session_download.element_id, "data", allow_duplicate=True),
        Input(fe.session_download.button_id, "n_clicks"),
        State(fe.mode_selection.element_id, "value"),
        State(fe.dimensionality_selection.element_id, "value"),
        State(fe.sizemode_selection.element_id, "value"),
        State(fe.scaling.element_id, "value"),
        State(fe.min_max_scaling.element_id, "value"),
        State(fe.linear_scaling.factor_element_id, "value"),
        State(fe.linear_scaling.base_element_id, "value"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.lipidome_grid.element_id, "virtualRowData"),
        State(fe.lipidome_grid.element_id, "columnDefs"),
        State(fe.lipidome_grid.element_id, "filterModel"),
        State(fe.lipid_grid.element_id, "rowData"),
        State(fe.lipid_grid.element_id, "virtualRowData"),
        State(fe.lipid_grid.element_id, "columnDefs"),
        State(fe.lipid_grid.element_id, "filterModel"),
        State(fe.difference_grid.element_id, "rowData"),
        State(fe.difference_grid.element_id, "columnDefs"),
        State(fe.difference_grid.element_id, "selectedRows"),
        State(fe.difference_grid.element_id, "filterModel"),
        State(fe.log2fc_grid.element_id, "rowData"),
        State(fe.log2fc_grid.element_id, "columnDefs"),
        State(fe.log2fc_grid.element_id, "selectedRows"),
        State(fe.log2fc_grid.element_id, "filterModel"),
        prevent_initial_call=True,
    )
    def download_session_callback(
        n_clicks: int,
        mode: Literal["lipidome", "difference", "log2fc"],
        dim: Literal[2, 3],
        sizemode: Literal["area", "diameter"],
        scaling_type: Literal["min_max", "linear"],
        min_max_scaling_value: tuple[int, int],
        linear_scaling_factor: float,
        linear_scaling_base: float,
        lipidome_records: list[dict],
        lipidome_virtual_records: list[dict],
        lipidome_col_groups_defs: list[dict],
        lipidome_filter_model: dict,
        lipid_records: list[dict],
        lipid_virtual_records: list[dict],
        lipid_col_groups_defs: list[dict],
        lipid_filter_model: dict,
        difference_records: list[dict],
        difference_col_groups_defs: list[dict],
        difference_selected_rows: list[dict],
        difference_filter_model: dict,
        log2fc_records: list[dict],
        log2fc_col_groups_defs: list[dict],
        log2fc_selected_rows: list[dict],
        log2fc_filter_model: dict,
    ) -> dict:
        scatter_cfg: ScatterCfg = ScatterCfg(
            mode=mode,
            dim=dim,
            sizemode=sizemode,
            scaling_method=scaling_type,
            min_max_scaling_value=min_max_scaling_value,
            linear_scaling_factor=linear_scaling_factor,
            linear_scaling_base=linear_scaling_base,
            template="",
        )

        gdc: GridDataCollection = GridDataCollection.from_records(
            lipidome_records=lipidome_records,
            lipidome_virtual_records=lipidome_virtual_records,
            lipidome_col_groups_defs=lipidome_col_groups_defs,
            lipidome_selected_rows=[],
            lipid_records=lipid_records,
            lipid_virtual_records=lipid_virtual_records,
            lipid_col_groups_defs=lipid_col_groups_defs,
            lipid_selected_rows=[],
            difference_records=difference_records,
            difference_virtual_records=[],
            difference_col_groups_defs=difference_col_groups_defs,
            difference_selected_rows=difference_selected_rows,
            log2fc_records=log2fc_records,
            log2fc_virtual_records=[],
            log2fc_col_groups_defs=log2fc_col_groups_defs,
            log2fc_selected_rows=log2fc_selected_rows,
        )

        session: SessionState = SessionState(
            gdc,
            scatter_cfg,
            lipidome_filter_model,
            lipid_filter_model,
            difference_filter_model,
            log2fc_filter_model,
        )

        contents: str = session.to_json()

        filename: str = "lipidome_projector_session.json"

        return dict(content=contents, filename=filename)

    @callback(
        Output(fe.mode_selection.element_id, "value", allow_duplicate=True),
        Output(
            fe.dimensionality_selection.element_id,
            "value",
            allow_duplicate=True,
        ),
        Output(
            fe.sizemode_selection.element_id, "value", allow_duplicate=True
        ),
        Output(fe.scaling.element_id, "value", allow_duplicate=True),
        Output(fe.min_max_scaling.element_id, "value", allow_duplicate=True),
        Output(
            fe.linear_scaling.factor_element_id, "value", allow_duplicate=True
        ),
        Output(
            fe.linear_scaling.base_element_id, "value", allow_duplicate=True
        ),
        Output(fe.lipidome_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.lipidome_grid.element_id, "virtualRowData", allow_duplicate=True
        ),
        Output(
            fe.lipidome_grid.element_id, "columnDefs", allow_duplicate=True
        ),
        Output(
            fe.lipidome_grid.element_id, "filterModel", allow_duplicate=True
        ),
        Output(fe.lipid_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.lipid_grid.element_id, "virtualRowData", allow_duplicate=True
        ),
        Output(fe.lipid_grid.element_id, "columnDefs", allow_duplicate=True),
        Output(fe.lipid_grid.element_id, "filterModel", allow_duplicate=True),
        Output(fe.difference_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.difference_grid.element_id,
            "virtualRowData",
            allow_duplicate=True,
        ),
        Output(
            fe.difference_grid.element_id, "columnDefs", allow_duplicate=True
        ),
        Output(
            fe.difference_grid.element_id, "selectedRows", allow_duplicate=True
        ),
        Output(
            fe.difference_grid.element_id, "filterModel", allow_duplicate=True
        ),
        Output(fe.log2fc_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.log2fc_grid.element_id, "virtualRowData", allow_duplicate=True
        ),
        Output(fe.log2fc_grid.element_id, "columnDefs", allow_duplicate=True),
        Output(
            fe.log2fc_grid.element_id, "selectedRows", allow_duplicate=True
        ),
        Output(fe.log2fc_grid.element_id, "filterModel", allow_duplicate=True),
        Output(fe.problem_modal.element_id, "is_open", allow_duplicate=True),
        Output(fe.problem_modal.element_id, "children", allow_duplicate=True),
        Input(fe.session_download.upload_id, "contents"),
        prevent_initial_call=True,
    )
    def upload_session_callback(contents: str) -> (
        tuple[
            Literal["lipidome", "difference", "log2fc"],
            Literal[2, 3],
            Literal["area", "diameter"],
            Literal["min_max", "linear"],
            tuple[int, int],
            float,
            float,
            list[dict],
            list[dict],
            list[dict],
            dict,
            list[dict],
            list[dict],
            list[dict],
            dict,
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            dict,
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            dict,
            NoUpdate,
            NoUpdate,
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
            NoUpdate,
            bool,
            str,
        ]
    ):
        if contents == "":
            raise PreventUpdate

        # TODO Extract decoding to utils.
        try:
            session: SessionState = SessionState.from_json(
                base64.b64decode(contents.split(",")[1]).decode()
            )
        except Exception as e:  # noqa: F841
            # TODO Extract text to config.
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
                no_update,
                True,
                "Error while decoding session data.",
            )

        return (
            session.scatter_cfg.mode,
            session.scatter_cfg.dim,
            session.scatter_cfg.sizemode,
            session.scatter_cfg.scaling_method,
            session.scatter_cfg.min_max_scaling_value,
            session.scatter_cfg.linear_scaling_factor,
            session.scatter_cfg.linear_scaling_base,
            session.gdc.lipidome_data.records,
            session.gdc.lipidome_data.virtual_records,
            session.gdc.lipidome_data.col_groups_defs,
            session.lipidome_filter_model,
            session.gdc.lipid_data.records,
            session.gdc.lipid_data.virtual_records,
            session.gdc.lipid_data.col_groups_defs,
            session.lipid_filter_model,
            session.gdc.difference_data.records,
            session.gdc.difference_data.virtual_records,
            session.gdc.difference_data.col_groups_defs,
            session.gdc.difference_data.selected_rows,
            session.difference_filter_model,
            session.gdc.log2fc_data.records,
            session.gdc.log2fc_data.virtual_records,
            session.gdc.log2fc_data.col_groups_defs,
            session.gdc.log2fc_data.selected_rows,
            session.log2fc_filter_model,
            no_update,
            no_update,
        )
