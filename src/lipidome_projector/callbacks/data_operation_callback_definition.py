"""Module concerning the definition of callbacks for data operations."""

import logging

from itertools import cycle

import plotly.express as px

from dash import Input, Output, State, callback, no_update
from dash._callback import NoUpdate

from embedding_visualization.colors import rgb_str_to_hex

from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.lipidome.dataset_processing import (
    add_grouping,
    add_pairwise_changes,
)
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)


logger: logging.Logger = logging.getLogger(__name__)


def reg_data_operation_callbacks_python(
    fe: FrontEnd, col_names: ColNames
) -> None:
    @callback(
        Output(fe.lipidome_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.grid_tabs.element_id, "value", allow_duplicate=True),
        Output(fe.lipidome_grid.element_id, "scrollTo", allow_duplicate=True),
        Output(fe.problem_modal.element_id, "is_open", allow_duplicate=True),
        Output(fe.problem_modal.body_id, "children", allow_duplicate=True),
        Input(fe.grouping_component.button_id, "n_clicks"),
        State(fe.grouping_component.dropdown_id, "value"),
        State(fe.grouping_component.input_id, "value"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.lipidome_grid.element_id, "selectedRows"),
        State(fe.lipidome_grid.element_id, "columnDefs"),
        State(fe.lipid_grid.element_id, "rowData"),
        State(fe.lipid_grid.element_id, "columnDefs"),
        prevent_initial_call=True,
    )
    def add_grouping_callback(
        n_clicks: int,
        aggregation_type: str,
        grouping_name: str,
        lipidome_records: list[dict],
        lipidome_selected_records: list[dict],
        lipidome_col_groups_defs: list[dict],
        lipid_records: list[dict],
        lipid_col_groups_defs: list[dict],
    ) -> (
        tuple[list[dict], str, dict[str, int], bool, NoUpdate]
        | tuple[NoUpdate, NoUpdate, NoUpdate, bool, str]
    ):
        if (
            lipidome_selected_records is None
            or len(lipidome_selected_records) < 2
        ):
            return (
                no_update,
                no_update,
                no_update,
                True,
                "Please select at least two lipidome rows.",
            )

        if not grouping_name:
            return (
                no_update,
                no_update,
                no_update,
                True,
                "Please provide a grouping name.",
            )

        if grouping_name in [
            record[col_names.lipidome] for record in lipidome_records
        ]:
            return (
                no_update,
                no_update,
                no_update,
                True,
                f"Name '{grouping_name}' already present in the dataset.",
            )

        lipidome_fe_data_input: LipidomeFrontEndData = LipidomeFrontEndData(
            lipidome_records=lipidome_records,
            lipidome_selected_records=lipidome_selected_records,
            lipidome_col_groups_defs=lipidome_col_groups_defs,
            lipid_records=lipid_records,
            lipid_virtual_records=lipid_records,
            lipid_col_groups_defs=lipid_col_groups_defs,
        )

        lipidome_fe_data_output: LipidomeFrontEndData = add_grouping(
            aggregation_type, grouping_name, lipidome_fe_data_input, col_names
        )

        grouping_index: int = len(lipidome_fe_data_output.lipidome_records) - 1

        return (
            lipidome_fe_data_output.lipidome_records,
            "lipidome",
            {"rowIndex": grouping_index},
            False,
            no_update,
        )

    @callback(
        Output(fe.difference_grid.element_id, "rowData", allow_duplicate=True),
        Output(
            fe.difference_grid.element_id, "columnDefs", allow_duplicate=True
        ),
        Output(fe.log2fc_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.log2fc_grid.element_id, "columnDefs", allow_duplicate=True),
        Output(fe.grid_tabs.element_id, "value", allow_duplicate=True),
        Output(fe.grid_tabs.change_tabs_id, "value", allow_duplicate=True),
        Output(fe.problem_modal.element_id, "is_open", allow_duplicate=True),
        Output(fe.problem_modal.body_id, "children", allow_duplicate=True),
        Input(fe.change_component.button_id, "n_clicks"),
        State(fe.change_component.dropdown_id, "value"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.lipidome_grid.element_id, "selectedRows"),
        State(fe.lipidome_grid.element_id, "columnDefs"),
        State(fe.lipid_grid.element_id, "rowData"),
        State(fe.lipid_grid.element_id, "columnDefs"),
        State(fe.difference_grid.element_id, "rowData"),
        State(fe.difference_grid.element_id, "columnDefs"),
        State(fe.log2fc_grid.element_id, "rowData"),
        State(fe.log2fc_grid.element_id, "columnDefs"),
        prevent_initial_call=True,
    )
    def compute_pairwise_changes(
        n_clicks: int,
        change_selection: str,
        lipidome_records: list[dict],
        lipidome_selected_records: list[dict],
        lipidome_col_groups_defs: list[dict],
        lipid_records: list[dict],
        lipid_col_groups_defs: list[dict],
        difference_records: list[dict],
        difference_col_groups_defs: list[dict],
        log2fc_records: list[dict],
        log2fc_col_groups_defs: list[dict],
    ) -> (
        tuple[
            list[dict],
            list[dict],
            list[dict],
            list[dict],
            str,
            str,
            bool,
            NoUpdate,
        ]
        | tuple[
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
        if (
            lipidome_selected_records is None
            or len(lipidome_selected_records) < 2
        ):
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                True,
                "Please select at least two lipidome rows.",
            )

        lipidome_fe_data_input: LipidomeFrontEndData = LipidomeFrontEndData(
            lipidome_records=lipidome_records,
            lipidome_selected_records=lipidome_selected_records,
            lipidome_col_groups_defs=lipidome_col_groups_defs,
            lipid_records=lipid_records,
            lipid_virtual_records=lipid_records,
            lipid_col_groups_defs=lipid_col_groups_defs,
            difference_records=difference_records,
            difference_col_groups_defs=difference_col_groups_defs,
            log2fc_records=log2fc_records,
            log2fc_col_groups_defs=log2fc_col_groups_defs,
        )

        lipidome_fe_data_output: LipidomeFrontEndData = add_pairwise_changes(
            change_selection, lipidome_fe_data_input, col_names
        )

        return (
            lipidome_fe_data_output.difference_records,
            lipidome_fe_data_output.difference_col_groups_defs,
            lipidome_fe_data_output.log2fc_records,
            lipidome_fe_data_output.log2fc_col_groups_defs,
            "change",
            change_selection,
            False,
            no_update,
        )

    @callback(
        Output(
            fe.lipidome_grid.element_id, "rowTransaction", allow_duplicate=True
        ),
        Input(fe.set_color_component.set_color_button_id, "n_clicks"),
        State(fe.set_color_component.set_color_picker_id, "value"),
        State(fe.lipidome_grid.element_id, "selectedRows"),
        prevent_initial_call=True,
    )
    def set_lipidome_color(
        n_clicks: int, color: str, selected_rows: list[dict]
    ) -> dict[str, list[dict]] | NoUpdate:
        if not selected_rows:
            return no_update

        for row in selected_rows:
            row[col_names.color] = color

        return {"update": selected_rows}

    @callback(
        Output(fe.lipidome_grid.element_id, "rowTransaction", allow_duplicate=True),
        Input(fe.set_color_component.color_scale_button_id, "n_clicks"),
        State(fe.lipidome_grid.element_id, "selectedRows"),
        State(fe.set_color_component.color_scale_dropdown_id, "value"),
        prevent_initial_call=True,
    )
    def change_color_scale(
        n_clicks: int, selected_rows: list[dict], colorscale: str
    ) -> dict[str, list[dict]] | NoUpdate:
        if not selected_rows or not colorscale:
            return no_update

        colors: list[str] = getattr(px.colors.qualitative, colorscale)

        colors: list[str] = [
            color if color.startswith("#") else rgb_str_to_hex(color)
            for color in colors
        ]

        for row, color in zip(selected_rows, cycle(colors)):
            row[col_names.color] = color

        return {"update": selected_rows}

    @callback(
        Output(fe.lipidome_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.difference_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.log2fc_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.problem_modal.element_id, "is_open", allow_duplicate=True),
        Output(fe.problem_modal.body_id, "children", allow_duplicate=True),
        Input(fe.set_name_component.button_element_id, "n_clicks"),
        State(fe.set_name_component.input_element_id, "value"),
        State(fe.lipidome_grid.element_id, "selectedRows"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.difference_grid.element_id, "rowData"),
        State(fe.log2fc_grid.element_id, "rowData"),
        prevent_initial_call=True,
    )
    def set_lipidome_name(
        n_clicks: int,
        new_name: str,
        selected_rows: list[dict],
        lipidome_records: list[dict],
        difference_records: list[dict],
        log2fc_records: list[dict],
    ) -> (
        tuple[
            list[dict],
            list[dict],
            list[dict],
            bool,
            NoUpdate,
        ]
        | tuple[
            NoUpdate,
            NoUpdate,
            NoUpdate,
            bool,
            str,
        ]
    ):
        if selected_rows is None or not new_name or len(selected_rows) != 1:
            return (
                no_update,
                no_update,
                no_update,
                True,
                (
                    "Please select exactly one lipidome row and provide "
                    "a unique name."
                ),
            )

        if new_name in [
            record[col_names.lipidome] for record in lipidome_records
        ]:
            return (
                no_update,
                no_update,
                no_update,
                True,
                f'"{new_name}" already present in the dataset.',
            )

        current_name: str = selected_rows[0][col_names.lipidome]

        for record in lipidome_records:
            if record[col_names.lipidome] == current_name:
                record[col_names.lipidome] = new_name

        for record in difference_records:
            if record[col_names.from_lipidome] == current_name:
                record[col_names.from_lipidome] = new_name
            if record[col_names.to_lipidome] == current_name:
                record[col_names.to_lipidome] = new_name

        for record in log2fc_records:
            if record[col_names.from_lipidome] == current_name:
                record[col_names.from_lipidome] = new_name
            if record[col_names.to_lipidome] == current_name:
                record[col_names.to_lipidome] = new_name

        return (
            lipidome_records,
            difference_records,
            log2fc_records,
            False,
            no_update,
        )

    @callback(
        Output(fe.lipidome_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.difference_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.log2fc_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.last_deleted_store.element_id, "data", allow_duplicate=True),
        Output(
            fe.delete_component.button_undo_id,
            "disabled",
            allow_duplicate=True,
        ),
        Output(fe.problem_modal.element_id, "is_open", allow_duplicate=True),
        Output(fe.problem_modal.body_id, "children", allow_duplicate=True),
        Input(fe.delete_component.button_id, "n_clicks"),
        State(fe.lipidome_grid.element_id, "selectedRows"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.difference_grid.element_id, "rowData"),
        State(fe.log2fc_grid.element_id, "rowData"),
        prevent_initial_call=True,
    )
    def delete_selected_lipidomes(
        n_clicks: int,
        selected_rows: list[dict],
        lipidome_records: list[dict],
        difference_records: list[dict],
        log2fc_records: list[dict],
    ) -> (
        tuple[list[dict], list[dict], list[dict], dict, bool, bool, NoUpdate]
        | tuple[NoUpdate, NoUpdate, NoUpdate, NoUpdate, NoUpdate, bool, str]
    ):
        if selected_rows is None or len(selected_rows) < 1:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                True,
                "Please select at least one lipidome row.",
            )

        deleted_names: list[str] = [
            record[col_names.lipidome] for record in selected_rows
        ]

        lipidome_records = [
            record
            for record in lipidome_records
            if record[col_names.lipidome] not in deleted_names
        ]

        difference_records = [
            record
            for record in difference_records
            if record[col_names.from_lipidome] not in deleted_names
            and record[col_names.to_lipidome] not in deleted_names
        ]

        log2fc_records = [
            record
            for record in log2fc_records
            if record[col_names.from_lipidome] not in deleted_names
            and record[col_names.to_lipidome] not in deleted_names
        ]

        return (
            lipidome_records,
            difference_records,
            log2fc_records,
            {row["ROW_ID"]: row for row in selected_rows},
            False,
            False,
            no_update,
        )

    @callback(
        Output(fe.lipidome_grid.element_id, "rowData", allow_duplicate=True),
        Output(fe.last_deleted_store.element_id, "data", allow_duplicate=True),
        Output(
            fe.delete_component.button_undo_id,
            "disabled",
            allow_duplicate=True,
        ),
        Output(fe.problem_modal.element_id, "is_open", allow_duplicate=True),
        Output(fe.problem_modal.body_id, "children", allow_duplicate=True),
        Input(fe.delete_component.button_undo_id, "n_clicks"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.last_deleted_store.element_id, "data"),
        prevent_initial_call=True,
    )
    def undo_last_delete_selected_lipidomes(
        n_clicks: int, lipidome_records: list[dict], last_deleted: dict
    ) -> (
        tuple[
            list[dict],
            None,
            bool,
            bool,
            NoUpdate,
        ]
        | tuple[NoUpdate, NoUpdate, NoUpdate, bool, str]
    ):
        if last_deleted is None or len(last_deleted) < 1:
            return (
                no_update,
                no_update,
                no_update,
                True,
                "No deleted rows to undo.",
            )

        for row_id in sorted(last_deleted, reverse=True):
            lipidome_records.append(last_deleted[row_id])

        return (
            lipidome_records,
            None,
            True,
            False,
            no_update,
        )
