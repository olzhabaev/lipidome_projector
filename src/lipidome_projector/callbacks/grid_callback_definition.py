"""Module concerning graph settings callbacks."""

import logging

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.grid_processing import (
    gen_lipidome_lipid_filtered_state,
)
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)


logger: logging.Logger = logging.getLogger(__name__)


def reg_grid_callbacks_python(fe: FrontEnd, col_names: ColNames) -> None:
    @callback(
        Output(fe.lipidome_grid.element_id, "columnState", allow_duplicate=True),
        Output(fe.difference_grid.element_id, "columnState", allow_duplicate=True),
        Output(fe.log2fc_grid.element_id, "columnState", allow_duplicate=True),
        Input(fe.lipid_grid.element_id, "virtualRowData"),
        State(fe.lipid_grid.element_id, "rowData"),
        State(fe.lipid_grid.element_id, "columnDefs"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.lipidome_grid.element_id, "virtualRowData"),
        State(fe.lipidome_grid.element_id, "columnDefs"),
        prevent_initial_call=True,
    )
    def filter_lipidome_lipids(
        lipid_virtual_records: list[dict],
        lipid_records: list[dict],
        lipid_col_groups_defs: list[dict],
        lipidome_records: list[dict],
        lipidome_virtual_records: list[dict],
        lipidome_col_groups_defs: list[dict],
    ) -> tuple[list[dict], list[dict], list[dict]]:
        if lipidome_records is None:
            raise PreventUpdate

        lipidome_fe_data: LipidomeFrontEndData = LipidomeFrontEndData(
            lipidome_records=lipidome_records,
            lipidome_virtual_records=lipidome_virtual_records,
            lipidome_col_groups_defs=lipidome_col_groups_defs,
            lipid_records=lipid_records,
            lipid_virtual_records=lipid_virtual_records,
            lipid_col_groups_defs=lipid_col_groups_defs,
        )

        lipidome_grid_col_state_update: list[dict]
        change_grid_col_state_update: list[dict]
        (
            lipidome_grid_col_state_update,
            change_grid_col_state_update,
        ) = gen_lipidome_lipid_filtered_state(
            lipidome_fe_data=lipidome_fe_data,
            col_names=col_names,
            lipidome_filter_source="virtual",
        )

        return (
            lipidome_grid_col_state_update,
            change_grid_col_state_update,
            change_grid_col_state_update,
        )
