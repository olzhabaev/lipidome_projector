"""Module concerning the processing of the scatter plot."""

import logging

from typing import Any

import pandas as pd

from plotly.graph_objects import Figure
from dash.exceptions import PreventUpdate

from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset

from lipidome_projector.graph.abundance_visualization import (
    generate_lipid_abundance_bar_chart,
)
from lipidome_projector.graph.graph_settings import GraphSettings
from lipidome_projector.graph.lipidome_plotly_scatter import (
    LipidomeScatterParameters,
    gen_lipidome_scatter,
)
from lipidome_projector.graph.structure_drawing import (
    get_lipid_structure_image,
)
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.grid_processing import (
    gen_ds_and_filters,
)
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.lipidome.unstacking import (
    get_unstacked_dataset_df,
    get_change_sample_unstacked_df,
)


logger: logging.Logger = logging.getLogger(__name__)


# TODO Consider composing inputs into class (go together often), move check.
def chk_scatter_possible(
    lipidome_fe_data: LipidomeFrontEndData,
    graph_settings: GraphSettings,
) -> bool:
    """Check if a scatter plot can be generated with the current
    settings and data.
    :param lipidome_fe_data: Lipidome front end data.
    :param graph_settings: Graph settings.
    :returns: True if a scatter plot can be generated, False otherwise.
    """
    if not lipidome_fe_data.grids_complete():
        return False

    if graph_settings.mode == "difference" and (
        lipidome_fe_data.difference_selected_rows is None
        or len(lipidome_fe_data.difference_selected_rows) != 1
    ):
        return False

    if graph_settings.mode == "log2fc" and (
        lipidome_fe_data.log2fc_selected_rows is None
        or len(lipidome_fe_data.log2fc_selected_rows) != 1
    ):
        return False

    return True


# TODO: Abstact to "HoverVisualResults" or similar.
def gen_hover_abundance_chart_and_structure_img(
    hoverData: dict,
    lipidome_fe_data: LipidomeFrontEndData,
    col_names: ColNames,
    template: str,
    fullscreen_size: dict,
) -> tuple[Figure, str, str]:
    """Generate a bar chart and a lipid structure image from the hover
    data.
    :param hoverData: Hover data.
    :param lipidome_fe_data: Lipidome front end data.
    :param col_names: Column names.
    :param template: Plotly template.
    :param fullscreen_size: Size the client's screen.
    :returns: Bar chart and lipid structure image.
    """
    lipidome_ds: LipidomeDataset
    lipidome_filter: pd.Index
    lipidome_ds, lipidome_filter, _ = gen_ds_and_filters(
        lipidome_fe_data, col_names, "virtual"
    )

    lipidome_colormap: dict[str, str] = _gen_lipidome_colormap(
        lipidome_ds, col_names.color
    )

    lipid: str = hoverData["points"][0]["customdata"][1]

    abundance_chart: Figure = generate_lipid_abundance_bar_chart(
        lipidome_ds.get_lipid_abundances(
            lipid,
            lipidomes=lipidome_filter,
        ),
        lipidome_colormap,
        template=template,
    )

    smiles: str = str(
        lipidome_ds.lipid_features_df.loc[lipid, col_names.smiles]
    )

    img_src_lr: str = (
        f"data:image/png;base64,{get_lipid_structure_image(smiles)}"  # noqa E501
    )

    img_src_hr: str = (
        f"data:image/png;base64,{get_lipid_structure_image(smiles, fullscreen_size)}"  # noqa E501
    )

    return (abundance_chart, img_src_lr, img_src_hr)


# TODO Move into abstraction.
def gen_scatter_from_grid_input(
    lipidome_fe_data: LipidomeFrontEndData,
    graph_settings: GraphSettings,
    col_names: ColNames,
) -> Figure:
    """Generate a scatter plot from the grid input.
    :param lipidome_fe_data: Lipidome front end data.
    :param graph_settings: Graph settings.
    :param col_names: Column names.
    :returns: Scatter plot.
    """
    lipidome_ds: LipidomeDataset
    lipidome_filter: pd.Index
    lipid_filter: pd.Index
    lipidome_ds, lipidome_filter, lipid_filter = gen_ds_and_filters(
        lipidome_fe_data, col_names, "virtual"
    )

    scaling_method: str | None
    scaling_params: dict[str, Any] | None
    scaling_method, scaling_params = _gen_scaling(graph_settings)

    if graph_settings.mode == "overlay":
        figure: Figure = _gen_overlay_scatter_from_lipidome_ds(
            lipidome_ds=lipidome_ds,
            col_names=col_names,
            dimensionality=graph_settings.dimensionality,
            sizemode=graph_settings.sizemode,
            scaling_method=scaling_method,
            scaling_params=scaling_params,
            lipidome_filter=lipidome_filter,
            lipid_filter=lipid_filter,
        )
    elif graph_settings.mode in ["difference", "log2fc"]:
        from_lipidome: str
        to_lipidome: str
        from_lipidome, to_lipidome = _det_from_to_lipidomes(
            lipidome_fe_data,
            graph_settings.mode,
            col_names.from_lipidome,
            col_names.to_lipidome,
        )
        figure: Figure = _gen_change_scatter_from_lipidome_ds(
            lipidome_ds=lipidome_ds,
            col_names=col_names,
            from_lipidome=from_lipidome,
            to_lipidome=to_lipidome,
            graph_settings=graph_settings,
            scaling_method=scaling_method,
            scaling_params=scaling_params,
            lipid_filter=lipid_filter,
        )
    else:
        raise ValueError(f"Mode {graph_settings.mode} not supported.")

    figure.update_layout(template=graph_settings.template)

    return figure


def _gen_scaling(
    graph_settings: GraphSettings,
) -> tuple[str | None, dict[str, Any] | None]:
    if graph_settings.mode == "difference":
        scaling_method: str | None = None
        scaling_params: dict[str, Any] | None = None
    elif graph_settings.scaling_method == "min-max":
        scaling_method: str | None = "min_max"
        scaling_params: dict[str, Any] | None = {
            "min_val": graph_settings.min_max_scaling_value[0],
            "max_val": graph_settings.min_max_scaling_value[1],
        }
    elif graph_settings.scaling_method == "linear":
        scaling_method: str | None = "linear"
        scaling_params: dict[str, Any] | None = {
            "factor": graph_settings.linear_scaling_factor,
            "base": graph_settings.linear_scaling_base,
        }
    else:
        raise ValueError(
            f"Scaling type {graph_settings.scaling_method} not supported."
        )

    return scaling_method, scaling_params


def _gen_overlay_scatter_from_lipidome_ds(
    lipidome_ds: LipidomeDataset,
    col_names: ColNames,
    dimensionality: int,
    scaling_method: str | None,
    scaling_params: dict[str, Any] | None,
    sizemode: str,
    lipidome_filter: pd.Index | None = None,
    lipid_filter: pd.Index | None = None,
) -> Figure:
    params: LipidomeScatterParameters = LipidomeScatterParameters(
        df=get_unstacked_dataset_df(lipidome_ds, col_names),
        abundance_col_name=col_names.abundance,
        lipid_col_name=col_names.lipid,
        lipidome_col_name=col_names.lipidome,
        category_col_name=col_names.lipid_category,
        class_col_name=col_names.lipid_class,
        vector_col_names_2d=col_names.vec_space_2d,
        vector_col_names_3d=col_names.vec_space_3d,
        lipidome_filter=lipidome_filter,
        lipid_filter=lipid_filter,
        marker_sizemode=sizemode,  # type: ignore
        scaling_method=scaling_method,
        scaling_params=scaling_params,
        dimensionality=dimensionality,
        lipidome_colormap=_gen_lipidome_colormap(lipidome_ds, col_names.color),
        legend_position="right",
        legend_type="grouped",
        legend_truncation=10,
    )

    figure: Figure = gen_lipidome_scatter(params)

    return figure


def _gen_change_scatter_from_lipidome_ds(
    lipidome_ds: LipidomeDataset,
    col_names: ColNames,
    from_lipidome: str,
    to_lipidome: str,
    graph_settings: GraphSettings,
    scaling_method: str | None,
    scaling_params: dict[str, Any] | None,
    lipid_filter: pd.Index | None = None,
) -> Figure:
    params: LipidomeScatterParameters = LipidomeScatterParameters(
        df=get_change_sample_unstacked_df(
            lipidome_ds=lipidome_ds,
            abundance_change_type=graph_settings.mode,  # type: ignore
            from_lipidome=from_lipidome,
            to_lipidome=to_lipidome,
            col_names=col_names,
        ),
        abundance_col_name=col_names.abundance,
        lipid_col_name=col_names.lipid,
        lipidome_col_name=col_names.lipidome,
        category_col_name=col_names.lipid_category,
        class_col_name=col_names.lipid_class,
        vector_col_names_2d=col_names.vec_space_2d,
        vector_col_names_3d=col_names.vec_space_3d,
        lipid_filter=lipid_filter,
        scaling_method=scaling_method,
        scaling_params=scaling_params,
        dimensionality=graph_settings.dimensionality,
        colortype="change",
        change_col_name=col_names.change,
        colorscale_name="bluered",
        marker_sizemin=10,
        colorscale_midpoint=0,
        legend_position="top",
        legend_truncation=10,
    )

    figure: Figure = gen_lipidome_scatter(params)

    return figure


def _det_from_to_lipidomes(
    lipidome_fe_data: LipidomeFrontEndData,
    mode: str,
    from_col_name: str,
    to_col_name: str,
) -> tuple[str, str]:
    if mode == "difference":
        change_records: list[dict] = lipidome_fe_data.difference_selected_rows
    elif mode == "log2fc":
        change_records: list[dict] = lipidome_fe_data.log2fc_selected_rows
    else:
        raise ValueError(f"Mode {mode} not supported.")

    from_lipidome: str = change_records[0][from_col_name]
    to_lipidome: str = change_records[0][to_col_name]

    return from_lipidome, to_lipidome


def _gen_lipidome_colormap(
    lipidome_ds: LipidomeDataset, color_col_name: str
) -> dict:
    lipidome_colormap: dict = lipidome_ds.lipidome_features_df[
        color_col_name
    ].to_dict()

    return lipidome_colormap


def select_lipid_grid(
    col_names: ColNames,
    selected_rows: dict,
    selected_data: dict,
    click_data: dict,
    lipid_records: list[dict],
) -> tuple[
    list[dict],
    dict[str, list[str]],
    dict[str, int],
]:
    """
    Select lipids in the grid.
    :param col_names: Column names.
    :param selected_rows: Selected rows.
    :param selected_data: Selected data.
    :param click_data: Click data.
    :param lipid_records: Lipid records.
    :returns: Reordered records, selected lipids, and row index.
    """
    already_selected_in_grid: list = (
        [row[col_names.lipid] for row in selected_rows]
        if selected_rows
        else []
    )

    if click_data:
        new_point = click_data["points"][0]["customdata"][1]
        if new_point in already_selected_in_grid:
            already_selected_in_grid.remove(new_point)
            click_data = None

    new_selected_on_graph: list = (
        selected_data["points"] if selected_data is not None else []
    ) + (click_data["points"] if click_data is not None else [])

    selected_lipids: list[str] = [
        point["customdata"][1] for point in new_selected_on_graph
    ] + already_selected_in_grid

    reordered_records: list[dict] = sorted(
        lipid_records,
        key=lambda r: r[col_names.lipid] not in selected_lipids,
    )

    return reordered_records, {"ids": selected_lipids}, {"rowIndex": 0}


def add_annotation(
    figure_dict: dict,
    col_names: ColNames,
    selected_rows: dict,
    dimensionality: int,
) -> Figure:
    """
    Add annotation to the figure.
    :param figure_dict: Figure dictionary.
    :param col_names: Column names.
    :param selected_rows: Selected rows.
    :param dimensionality: Dimensionality.
    :returns: Figure with annotation.
    """

    figure: Figure = Figure(figure_dict)

    selected_lipids: list = [row[col_names.lipid] for row in selected_rows]
    selected_lipids_set: set = set(selected_lipids)
    idx_selected_lipids: list = []
    for idx, lipid in enumerate(figure["data"][0]["customdata"]):
        if lipid[1] in selected_lipids_set:
            idx_selected_lipids.append(idx)
            selected_lipids_set.remove(lipid[1])

    selected_lipids_x: list = [
        figure["data"][0]["x"]["_inputArray"][str(lipid_idx)]
        for lipid_idx in idx_selected_lipids
    ]
    selected_lipids_y: list = [
        figure["data"][0]["y"]["_inputArray"][str(lipid_idx)]
        for lipid_idx in idx_selected_lipids
    ]

    selected_lipid_names: list = [
        figure["data"][0]["customdata"][lipid_idx][1]
        for lipid_idx in idx_selected_lipids
    ]
    if dimensionality == 2:

        figure_dict["layout"]["annotations"]: list = []
        figure: Figure = Figure(figure_dict)

        for i, (x, y) in enumerate(zip(selected_lipids_x, selected_lipids_y)):
            figure.add_annotation(
                x=x,
                y=y,
                xref="x",
                yref="y",
                text=selected_lipid_names[i],
                showarrow=True,
                captureevents=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="Black",
                font={"size": 15},
                ax=30,
                ay=-30,
            )
    elif dimensionality == 3:
        figure: Figure = Figure(figure_dict)

        selected_lipids_z: list = [
            figure["data"][0]["z"]["_inputArray"][str(lipid_idx)]
            for lipid_idx in idx_selected_lipids
        ]

        figure_dict["layout"]["scene"]["annotations"]: list = []
        figure: Figure = Figure(figure_dict)

        annotations: list = [
            {
                "showarrow": True,
                "x": x,
                "y": y,
                "z": z,
                "text": selected_lipid_names[i],
                "arrowhead": 2,
                "arrowsize": 1,
                "arrowwidth": 2,
                "captureevents": True,
                "arrowcolor": "Black",
                "font": {"size": 15},
                "ax": 30,
                "ay": -30,
            }
            for i, (x, y, z) in enumerate(
                zip(
                    selected_lipids_x,
                    selected_lipids_y,
                    selected_lipids_z,
                )
            )
        ]

        figure.update_layout(scene={"annotations": annotations})

    return figure
