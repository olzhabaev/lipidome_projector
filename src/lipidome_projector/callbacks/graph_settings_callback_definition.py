"""Module concerning graph settings callbacks."""

import logging

from typing import cast

from dash import (
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    ClientsideFunction,
    no_update,
)
from dash._callback import NoUpdate
from plotly.graph_objects import Figure
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.graph.graph_settings import GraphSettings
from lipidome_projector.graph.scatter_processing import (
    chk_scatter_possible,
    gen_scatter_from_grid_input,
    gen_hover_abundance_chart_and_structure_img,
    add_annotation,
)
from lipidome_projector.graph.lipidome_plotly_scatter import gen_empty_plot
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)


logger: logging.Logger = logging.getLogger(__name__)


def reg_graph_settings_callbacks_python(
    fe: FrontEnd, col_names: ColNames
) -> None:
    @callback(
        Output(fe.lipidome_graph.element_id, "figure", allow_duplicate=True),
        Input(fe.mode_selection.element_id, "value"),
        Input(fe.dimensionality_selection.element_id, "value"),
        Input(fe.sizemode_selection.element_id, "value"),
        Input(fe.scaling.element_id, "value"),
        Input(fe.min_max_scaling.element_id, "value"),
        Input(fe.linear_scaling.factor_element_id, "value"),
        Input(fe.linear_scaling.base_element_id, "value"),
        State(fe.lipidome_grid.element_id, "rowData"),
        Input(fe.lipidome_grid.element_id, "virtualRowData"),
        State(fe.lipidome_grid.element_id, "columnDefs"),
        State(fe.lipid_grid.element_id, "rowData"),
        Input(fe.lipid_grid.element_id, "virtualRowData"),
        State(fe.lipid_grid.element_id, "columnDefs"),
        State(fe.difference_grid.element_id, "rowData"),
        State(fe.difference_grid.element_id, "columnDefs"),
        Input(fe.difference_grid.element_id, "selectedRows"),
        State(fe.log2fc_grid.element_id, "rowData"),
        State(fe.log2fc_grid.element_id, "columnDefs"),
        Input(fe.log2fc_grid.element_id, "selectedRows"),
        Input(fe.theme_switch.theme_name, "children"),
        prevent_initial_call=True,
    )
    def refresh_graph(
        mode: str,
        dimensionality: int,
        sizemode: str,
        scaling_type: str,
        min_max_scaling_value: tuple[float, float],
        linear_scaling_factor: float,
        linear_scaling_base: float,
        lipidome_records: list[dict],
        lipidome_virtual_records: list[dict],
        lipidome_column_groups_defs: list[dict],
        lipid_records: list[dict],
        lipid_virtual_records: list[dict],
        lipid_column_groups_defs: list[dict],
        difference_records: list[dict],
        difference_column_groups_defs: list[dict],
        difference_selected_rows: list[dict],
        log2fc_records: list[dict],
        log2fc_column_groups_defs: list[dict],
        log2fc_selected_rows: list[dict],
        theme: str,
    ) -> Figure | dict:

        load_figure_template(theme)

        if not lipidome_records:
            return gen_empty_plot()

        lipidome_fe_data: LipidomeFrontEndData = LipidomeFrontEndData(
            lipidome_records=lipidome_records,
            lipidome_virtual_records=lipidome_virtual_records,
            lipidome_col_groups_defs=lipidome_column_groups_defs,
            lipid_records=lipid_records,
            lipid_virtual_records=lipid_virtual_records,
            lipid_col_groups_defs=lipid_column_groups_defs,
            difference_records=difference_records,
            difference_col_groups_defs=difference_column_groups_defs,
            difference_selected_rows=difference_selected_rows,
            log2fc_records=log2fc_records,
            log2fc_col_groups_defs=log2fc_column_groups_defs,
            log2fc_selected_rows=log2fc_selected_rows,
        )

        graph_settings: GraphSettings = GraphSettings(
            mode=mode,
            dimensionality=dimensionality,
            sizemode=sizemode,
            scaling_method=scaling_type,
            min_max_scaling_value=min_max_scaling_value,
            linear_scaling_factor=linear_scaling_factor,
            linear_scaling_base=linear_scaling_base,
            template=cast(str, theme),
        )

        if not chk_scatter_possible(lipidome_fe_data, graph_settings):
            return gen_empty_plot()

        figure: Figure = gen_scatter_from_grid_input(
            lipidome_fe_data=lipidome_fe_data,
            graph_settings=graph_settings,
            col_names=col_names,
        )

        return figure

    @callback(
        Output(fe.abundance_graph.element_id, "figure"),
        Output(fe.structure_image.element_id, "src"),
        Output(fe.structure_image_fullscreen_modal.content_id, "src"),
        Input(fe.lipidome_graph.element_id, "hoverData"),
        Input(fe.theme_switch.theme_name, "children"),
        State(fe.lipidome_grid.element_id, "rowData"),
        State(fe.lipidome_grid.element_id, "virtualRowData"),
        State(fe.lipidome_grid.element_id, "columnDefs"),
        State(fe.lipid_grid.element_id, "rowData"),
        State(fe.lipid_grid.element_id, "virtualRowData"),
        State(fe.lipid_grid.element_id, "columnDefs"),
        State(fe.difference_grid.element_id, "rowData"),
        State(fe.difference_grid.element_id, "columnDefs"),
        State(fe.log2fc_grid.element_id, "rowData"),
        State(fe.log2fc_grid.element_id, "columnDefs"),
        State(fe.fullscreen_size_store.element_id, "data"),
        prevent_initial_call=True,
    )
    def display_hover(
        hoverData: dict,
        theme: str,
        lipidome_records: list[dict],
        lipidome_virutal_records: list[dict],
        lipidome_column_groups_defs: list[dict],
        lipid_records: list[dict],
        lipid_virtual_records: list[dict],
        lipid_column_groups_defs: list[dict],
        difference_records: list[dict],
        difference_column_groups_defs: list[dict],
        log2fc_records: list[dict],
        log2fc_column_groups_defs: list[dict],
        fullscreen_size: dict,
    ) -> tuple[Figure, str, str] | tuple[dict, str, NoUpdate]:
        lipidome_fe_data: LipidomeFrontEndData = LipidomeFrontEndData(
            lipidome_records=lipidome_records,
            lipidome_virtual_records=lipidome_virutal_records,
            lipidome_col_groups_defs=lipidome_column_groups_defs,
            lipid_records=lipid_records,
            lipid_virtual_records=lipid_virtual_records,
            lipid_col_groups_defs=lipid_column_groups_defs,
            difference_records=difference_records,
            difference_col_groups_defs=difference_column_groups_defs,
            log2fc_records=log2fc_records,
            log2fc_col_groups_defs=log2fc_column_groups_defs,
        )

        if hoverData is None:
            raise PreventUpdate

        # Note: If this callback is to be replaced by a client-side
        # callback, structure images have to be pre-generated and
        # stored in the grid data. Within the function call
        # the images are then to be retrieved from the grid data
        # rather than generated server-side.
        return gen_hover_abundance_chart_and_structure_img(
            hoverData=hoverData,
            lipidome_fe_data=lipidome_fe_data,
            template=cast(str, theme),
            col_names=col_names,
            fullscreen_size=fullscreen_size,
        )

    @callback(
        Output(fe.linear_scaling.factor_element_id, "min"),
        Output(fe.linear_scaling.factor_element_id, "max"),
        Output(fe.linear_scaling.factor_element_id, "value"),
        Output(fe.linear_scaling.base_element_id, "min"),
        Output(fe.linear_scaling.base_element_id, "max"),
        Output(fe.linear_scaling.base_element_id, "value"),
        Output(fe.min_max_scaling.element_id, "min"),
        Output(fe.min_max_scaling.element_id, "max"),
        Output(fe.min_max_scaling.element_id, "value"),
        Input(fe.sizemode_selection.element_id, "value"),
        Input(fe.lipidome_grid.element_id, "rowData"),
        prevent_initial_call=True,
    )
    def adjust_sizemode_scaling_ranges(
        sizemode: str,
        lipidome_records: list[dict],
    ) -> tuple[int, int, int, int, int, int, int, int, tuple[int, int]]:

        def _adjust_scaling_ranges(
            sizemode: str, max_value: float
        ) -> tuple[int, int, int, int, int, int, int, int, tuple[int, int]]:
            """
            Workaround for bug in Plotly's marker sizes:
            https://github.com/plotly/plotly.py/issues/4556
            """
            factor_min: int = getattr(
                fe.linear_scaling, f"factor_min_{sizemode}"
            )
            factor_max: int = getattr(
                fe.linear_scaling, f"factor_max_{sizemode}"
            )
            base_max: int = getattr(fe.linear_scaling, f"base_max_{sizemode}")
            factor_value: int = getattr(
                fe.linear_scaling, f"factor_value_{sizemode}"
            )
            base_min: int = getattr(fe.linear_scaling, f"base_min_{sizemode}")
            base_value: int = getattr(
                fe.linear_scaling, f"base_value_{sizemode}"
            )
            min_scaling: int = getattr(fe.min_max_scaling, f"min_{sizemode}")
            max_scaling: int = getattr(fe.min_max_scaling, f"max_{sizemode}")
            value_scaling: tuple[int, int] = getattr(
                fe.min_max_scaling, f"value_{sizemode}"
            )

            max_result: float = max_value * factor_max + base_max

            factor_max: int = (
                factor_max
                if max_result < 10000
                else int((10000 - base_max) / max_value)
            )

            return (
                factor_min,
                factor_max,
                factor_value,
                base_min,
                base_max,
                base_value,
                min_scaling,
                max_scaling,
                value_scaling,
            )

        try:
            values: list = [
                value
                for record in lipidome_records
                for value in record.values()
                if isinstance(value, (int, float))
            ]
            max_value: float | int = max(values)
        except ValueError:
            logger.warning(
                "Could not adjust maximum factor for linear scaling."
            )
            max_value: int = 1

        if sizemode in ["area", "diameter"]:
            return _adjust_scaling_ranges(sizemode, max_value)
        else:
            raise ValueError(f"Sizemode {sizemode} not supported.")

    # TODO Re-activate callback, when annotation persistence is implemented.
    # @callback(
    #     Output(fe.lipidome_graph.element_id, "figure", allow_duplicate=True),
    #     Input(fe.lipidome_graph.element_id, "clickData"),
    #     State(fe.lipidome_graph.element_id, "figure"),
    #     State(fe.dimensionality_selection.element_id, "value"),
    #     prevent_initial_call=True,
    # )
    # def annotate_click_data(
    #     clickData: dict, figure_dict: dict, dimensionality: int
    # ) -> Figure | NoUpdate:
    #     if clickData is None:
    #         return no_update

    #     return add_annotation(
    #         clickData=clickData,
    #         figure_dict=figure_dict,
    #         dimensionality=dimensionality,
    #     )

    clientside_callback(
        ClientsideFunction(
            namespace="clientside",
            function_name="invert_structure_image_bg_on_dark_theme",
        ),
        Output(
            fe.theme_switch.switch_id,
            "className",
            allow_duplicate=True,
        ),
        Input(fe.structure_image.element_id, "src"),
        Input(fe.theme_switch.theme_name, "children"),
        State(fe.structure_image.element_id, "id"),
        prevent_initial_call=True,
    )

    clientside_callback(
        ClientsideFunction(
            namespace="clientside",
            function_name="trunc_legend_and_add_tooltip",
        ),
        Output(fe.lipidome_graph.element_id, "className"),
        Input(fe.lipidome_graph.element_id, "figure"),
        State(fe.lipidome_graph.element_id, "id"),
    )

    clientside_callback(
        ClientsideFunction(
            namespace="clientside",
            function_name="trunc_legend_and_add_tooltip",
        ),
        Output(fe.lipidome_graph_fullscreen_modal.content_id, "className"),
        Input(fe.lipidome_graph_fullscreen_modal.content_id, "figure"),
        State(fe.lipidome_graph_fullscreen_modal.content_id, "id"),
    )

    @callback(
        Output(fe.abundance_graph_fullscreen_modal.element_id, "is_open"),
        Output(fe.abundance_graph_fullscreen_modal.content_id, "figure"),
        Input(fe.abundance_graph_fullscreen_button.element_id, "n_clicks"),
        State(fe.abundance_graph.element_id, "figure"),
        prevent_initial_call=True,
    )
    def open_abundance_graph_fullscreen_modal(
        n_clicks: int, figure: Figure
    ) -> tuple[bool, Figure]:
        return True, figure

    @callback(
        Output(fe.lipidome_graph_fullscreen_modal.element_id, "is_open"),
        Output(fe.lipidome_graph_fullscreen_modal.content_id, "figure"),
        Input(fe.lipidome_graph_fullscreen_button.element_id, "n_clicks"),
        State(fe.lipidome_graph.element_id, "figure"),
        prevent_initial_call=True,
    )
    def open_lipidome_graph_fullscreen_modal(
        n_clicks: int, figure: Figure
    ) -> tuple[bool, Figure]:
        return True, figure

    @callback(
        Output(fe.structure_image_fullscreen_modal.element_id, "is_open"),
        Input(fe.structure_image_fullscreen_button.element_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_structure_image_fullscreen_modal(n_clicks: int) -> bool:
        return True

    @callback(
        Output(fe.lipid_grid.element_id, "rowData"),
        Output(fe.lipid_grid.element_id, "selectedRows"),
        Output(fe.lipid_grid.element_id, "scrollTo"),
        Output(fe.grid_tabs.element_id, "value", allow_duplicate=True),
        Input(fe.lipidome_graph.element_id, "selectedData"),
        Input(fe.lipidome_graph.element_id, "clickData"),
        State(fe.lipid_grid.element_id, "rowData"),
        prevent_initial_call=True,
    )
    def highlight_selected_lipids(
        selected_data: dict, click_data: dict, lipid_records: list[dict]
    ) -> tuple[
        list[dict],
        dict[str, list[str]],
        dict[str, int],
        str,
    ]:
        points: list = (
            selected_data["points"] if selected_data is not None else []
        ) + (click_data["points"] if click_data is not None else [])

        if len(points) == 0:
            raise PreventUpdate

        selected_lipids: list[str] = [
            point["customdata"][1] for point in points
        ]

        reordered_records: list[dict] = sorted(
            lipid_records,
            key=lambda r: r[col_names.lipid] not in selected_lipids,
        )

        return (
            reordered_records,
            {"ids": selected_lipids},
            {"rowIndex": 0},
            fe.grid_tabs.lipid_tab_name,
        )

    clientside_callback(
        ClientsideFunction(
            namespace="clientside",
            function_name="update_figure_config",
        ),
        Output(fe.lipidome_graph.element_id, "figure"),
        Output(fe.lipidome_graph.element_id, "config"),
        Input(fe.figure_download_settings.name_input_id, "value"),
        Input(fe.figure_download_settings.file_type_dropdown_id, "value"),
        Input(fe.figure_download_settings.width_input_id, "value"),
        Input(fe.figure_download_settings.height_input_id, "value"),
        Input(fe.figure_download_settings.scale_factor_input_id, "value"),
        State(fe.lipidome_graph.element_id, "figure"),
        prevent_initial_call=True,
    )
