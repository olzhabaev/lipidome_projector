"""Module concerning the default dataset callbacks."""

import logging

from dash import Input, Output, State, callback

from lipidome_projector.lipidome.default_dataset_processing import (
    DefaultLipidomeData,
)
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.front_end.front_end_coordination import FrontEnd


logger: logging.Logger = logging.getLogger(__name__)


def reg_default_dataset_callbacks_python(
    fe: FrontEnd,
    default_lipidome_data: DefaultLipidomeData,
) -> None:
    logger.info("Register default dataset python callbacks.")

    @callback(
        Output(fe.default_dataset_modal.element_id, "is_open"),
        Input(fe.default_dataset_button.element_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_default_dataset_modal(n_clicks: int) -> bool:
        return True

    @callback(
        Output(
            fe.default_dataset_modal.dataset_description_div_element_id,
            "children",
        ),
        Input(fe.default_dataset_modal.selection_dropdown_element_id, "value"),
        prevent_initial_call=True,
    )
    def update_default_dataset_description(
        dataset_name: str | None,
    ) -> str:
        if dataset_name is None:
            return ""
        else:
            return default_lipidome_data._dataset_descriptions[dataset_name]

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
        Input(
            fe.default_dataset_modal.load_dataset_button_element_id, "n_clicks"
        ),
        State(fe.default_dataset_modal.selection_dropdown_element_id, "value"),
        prevent_initial_call=True,
    )
    def load_default_dataset_callback(
        n_clicks: int,
        dataset_name: str,
    ) -> tuple[
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
    ]:
        lipidome_fe_data: LipidomeFrontEndData = (
            default_lipidome_data.load_default_dataset(dataset_name)
        )

        return (
            lipidome_fe_data.lipidome_records,
            lipidome_fe_data.lipidome_records,
            lipidome_fe_data.lipidome_col_groups_defs,
            lipidome_fe_data.lipid_records,
            lipidome_fe_data.lipid_records,
            lipidome_fe_data.lipid_col_groups_defs,
            lipidome_fe_data.difference_records,
            lipidome_fe_data.difference_records,
            lipidome_fe_data.difference_col_groups_defs,
            lipidome_fe_data.log2fc_records,
            lipidome_fe_data.log2fc_records,
            lipidome_fe_data.log2fc_col_groups_defs,
        )
