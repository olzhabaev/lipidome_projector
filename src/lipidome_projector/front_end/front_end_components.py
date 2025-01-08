"""Module concerning the front end configuration."""

import logging

from abc import ABC, abstractmethod
from base64 import b64encode
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Literal, Any, Self
from zlib import decompress
from datetime import datetime

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px

from dash import (
    dcc,
    html,
    clientside_callback,
    ClientsideFunction,
    Output,
    Input,
    State,
    callback,
    no_update,
    ctx,
)
from dash._callback import NoUpdate
from dash.development.base_component import Component
from dash_split import Split
from dash.exceptions import PreventUpdate

from embedding_visualization.colors import rgb_str_to_hex

from lipidome_projector.graph.lipidome_plotly_scatter import gen_empty_plot


logger: logging.Logger = logging.getLogger(__name__)


# TODO Major clean-up.
# TODO Split into appropriate modules.

# COMMON BASE COMPONENT CLASSES -----------------------------------------------


@dataclass(frozen=True, kw_only=True)
class ComponentWrapper(ABC):
    element_id: str
    frame_title: str | None = None

    def get_component(self, *args, **kwargs) -> Component:
        component: Component = self.gen_component(*args, **kwargs)

        if self.frame_title is not None:
            component = self.frame_component(component)

        return component

    def frame_component(self, component: Component) -> Component:
        return html.Fieldset(
            className="fieldset",
            children=[html.Legend(self.frame_title), component],
        )

    @abstractmethod
    def gen_component(self, *args, **kwargs) -> Component: ...


@dataclass(frozen=True)
class Button(ComponentWrapper):
    element_id: str
    text: str
    disabled: bool = False

    def gen_component(self) -> dbc.Button:
        button = dbc.Button(
            self.text, id=self.element_id, disabled=self.disabled
        )

        return button


@dataclass(frozen=True)
class FullscreenButton(ComponentWrapper):
    element_id: str

    def gen_component(self) -> dbc.Button:
        fullscreen_button = dbc.Button(
            html.Span("\u21F1"),  # upwards arrow to the corner symbol
            id=self.element_id,
            class_name="fullscreen-button",
        )

        return fullscreen_button


@dataclass(frozen=True)
class Graph(ComponentWrapper):
    element_id: str

    def gen_component(self):
        graph = dcc.Graph(
            id=self.element_id,
            responsive=True,
            figure=gen_empty_plot(),
            config={
                "editable": True,
                "edits": {
                    "annotationPosition": False,
                    "annotationTail": True,
                    "annotationText": True,
                    "axisTitleText": False,
                    "colorbarPosition": False,
                    "colorbarTitleText": False,
                    "legendPosition": True,
                    "legendText": False,
                    "shapePosition": True,
                    "titleText": False,
                },
                "displaylogo": False,
                "toImageButtonOptions": {
                    "format": "svg",
                    "height": 800,
                    "width": 800,
                    "scale": 1,
                },
            },
            style={"height": "100%"},
        )

        return graph


@dataclass(frozen=True)
class Grid(ComponentWrapper):
    element_id: str

    def gen_component(self, row_id_col_name: str | None = None) -> dag.AgGrid:
        row_id: str | None = (
            f"params.data.{row_id_col_name}" if row_id_col_name else None
        )

        grid: dag.AgGrid = dag.AgGrid(
            id=self.element_id,
            dashGridOptions={"rowSelection": "multiple"},
            getRowId=row_id,
            style={"height": "100%"},
            className="ag-theme-alpine compact",
        )

        return grid


@dataclass(frozen=True)
class UploadComponent(ComponentWrapper):
    element_id: str
    text: str

    def gen_component(self) -> dcc.Upload:
        style: dict[str, str] = {
            "width": "50%",
            "height": "40px",
            "lineHeight": "20px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
        }

        upload_component: dcc.Upload = dcc.Upload(
            id=self.element_id,
            children=html.Div([html.A(self.text)]),
            style=style,
            multiple=False,
        )

        return upload_component


@dataclass(frozen=True)
class Tooltip(ComponentWrapper):
    element_id: str
    placement: str
    text: str

    def gen_component(self, target: str) -> dbc.Tooltip:
        tooltip = dbc.Tooltip(
            self.text, placement=self.placement, target=target
        )

        return tooltip


@dataclass(frozen=True)
class TriggerDiv(ComponentWrapper):
    element_id: str

    def gen_component(self) -> html.Div:
        trigger_div: html.Div = html.Div(
            id=self.element_id, style={"display": "none"}
        )

        return trigger_div


# CONCRETE COMPONENT CLASSES --------------------------------------------------


# -- MISC. COMPONENTS ---------------------------------------------------------


@dataclass(frozen=True)
class PreventFigureRefresh(TriggerDiv):
    element_id: str = "prevent-figure-refresh"


@dataclass(frozen=True)
class SplitVertical(Split):
    element_id: str = "split-vertical"

    def gen_component(self, children: list[Component]) -> Split:
        split = Split(
            id=self.element_id,
            direction="vertical",
            sizes=(70, 30),
            children=children,
        )

        return split


@dataclass(frozen=True)
class SplitHorizontal(Split):
    element_id: str = "split-horizontal"

    def gen_component(self, children: list[Component]) -> Split:
        split = Split(
            id=self.element_id,
            direction="horizontal",
            sizes=(70, 30),
            children=children,
        )

        return split


@dataclass(frozen=True)
class FullScreenSizeStore(ComponentWrapper):
    element_id: str = "fullscreen-size-store"

    def gen_component(self) -> dcc.Store:
        store = dcc.Store(
            id=self.element_id,
            data={},
        )

        return store

    def __post_init__(self):
        clientside_callback(
            """
            function(data) {
                if(data === null) {
                    return dash_clientside.no_update;
                }
                var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
                var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
                return {
                    'width': width - 150, 'height': height - 150
                };
            }
            """,  # noqa: E501
            Output(self.element_id, "data"),
            Input(self.element_id, "data"),
        )


class FullscreenModal(ComponentWrapper):
    element_id: str
    content_type: type[Component]
    content_id: str
    title: str = ""
    is_open: bool = False

    def gen_component(self) -> dbc.Modal:
        if self.content_type == dcc.Graph:
            modal_content = self.content_type(
                id=self.content_id,
                responsive=True,
                figure=gen_empty_plot(),
                config={
                    "displaylogo": False,
                    "toImageButtonOptions": {
                        "format": "svg",
                        "width": 800,
                        "height": 800,
                    },
                },
                style={"height": "100%"},
            )
        else:
            modal_content = self.content_type(
                id=self.content_id, style={"height": "100%"}
            )
        fullscreen_modal: dbc.Modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(self.title)),
                dbc.ModalBody(modal_content),
            ],
            id=self.element_id,
            fullscreen=True,
            is_open=self.is_open,
        )

        return fullscreen_modal


@dataclass(frozen=True)
class FullScreenModalAbundanceGraph(FullscreenModal):
    element_id: str = "fullscreen-modal-abundance-graph"
    content_id: str = "fullscreen-modal-abundance-graph-body"
    content_type: type[Component] = dcc.Graph
    title: str = "Abundance Graph"


@dataclass(frozen=True)
class FullScreenModalLipidomeGraph(FullscreenModal):
    element_id: str = "fullscreen-modal-lipidome-graph"
    content_id: str = "fullscreen-modal-lipidome-graph-body"
    content_type: type[Component] = dcc.Graph
    title: str = "Lipidome Graph"


@dataclass(frozen=True)
class FullScreenModalStructureImage(FullscreenModal):
    element_id: str = "fullscreen-modal-structure-image"
    content_id: str = "fullscreen-modal-structure-image-body"
    content_type: type[Component] = html.Img
    title: str = "Chemical Structure"


@dataclass(frozen=True)
class TestWarning(ComponentWrapper):
    element_id: str = "test-warning"
    title: str = "Warning"
    text: str = (
        "'Lipidome Projector' is currently being developed. "
        "This is a preliminary test version of the software. "
        "It is not intended for production use. "
        "Bugs are to be expected and some core features "
        "such as the annotation of lipid markers are not yet active."
    )
    size: Literal["sm", "lg", "xl"] = "xl"
    is_open: bool = True

    def gen_component(self) -> dbc.Modal:
        test_warning_modal: dbc.Modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(self.title)),
                dbc.ModalBody([html.Div(children=self.text)]),
            ],
            id=self.element_id,
            size=self.size,
            is_open=self.is_open,
        )

        return test_warning_modal


@dataclass(frozen=True)
class ProblemModal(ComponentWrapper):
    element_id: str = "problem-modal"
    body_id: str = "problem-modal-body"
    title: str = "A Problem Occurred"
    size: Literal["sm", "lg", "xl"] = "xl"
    is_open: bool = False

    def gen_component(self) -> dbc.Modal:
        problem_modal: dbc.Modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(self.title)),
                dbc.ModalBody(id=self.body_id),
            ],
            id=self.element_id,
            size=self.size,
            is_open=self.is_open,
        )

        return problem_modal

    def __post_init__(self):
        clientside_callback(
            """
            function (is_open, body_children) {
                if (is_open) {
                    return body_children;
                } else {
                    return "";
                }
            }
            """,
            Output(self.body_id, "children", allow_duplicate=True),
            Input(self.element_id, "is_open"),
            State(self.body_id, "children"),
            prevent_initial_call=True,
        )


@dataclass(frozen=True)
class StoreInit(ComponentWrapper):
    element_id: str = "store-init"

    def gen_component(self) -> dcc.Store:
        store = dcc.Store(id=self.element_id, data=True)

        return store


# -- GRAPH RELATED COMPONENTS -------------------------------------------------


@dataclass(frozen=True)
class LipidomeGraph(Graph):
    element_id: str = "lipidome-graph"


@dataclass(frozen=True)
class LipidomeGraphFullscreenButton(FullscreenButton):
    element_id: str = "lipid-graph-fullscreen-button"


@dataclass(frozen=True)
class AbundanceGraph(Graph):
    element_id: str = "abundance-graph"


@dataclass(frozen=True)
class AbundanceGraphFullscreenButton(FullscreenButton):
    element_id: str = "abundance-graph-fullscreen-button"


@dataclass(frozen=True)
class StructureImage(ComponentWrapper):
    element_id: str = "structure-image"
    default_image_path: Path = (
        files("lipidome_projector.assets").joinpath("default_structure.png")
    )

    def gen_component(self) -> html.Img:
        encoded_image = b64encode(
            open(self.default_image_path, "rb").read()
        ).decode("ascii")
        image: html.Img = html.Img(
            src="data:image/png;base64,{}".format(encoded_image),
            style={"height": "50%", "width": "50%"},
            id=self.element_id,
        )

        return image


@dataclass(frozen=True)
class StructureImageFullscreenButton(FullscreenButton):
    element_id: str = "structure-image-fullscreen-button"


# -- GRID RELATED COMPONENTS --------------------------------------------------


@dataclass(frozen=True)
class LipidomeGrid(Grid):
    element_id: str = "lipidome-grid"


@dataclass(frozen=True)
class LipidGrid(Grid):
    element_id: str = "lipid-grid"


@dataclass(frozen=True)
class DifferenceGrid(Grid):
    element_id: str = "difference-grid"


@dataclass(frozen=True)
class Log2FCGrid(Grid):
    element_id: str = "log2fc-grid"


@dataclass(frozen=True)
class GridTabs(ComponentWrapper):
    element_id: str = "grid-tabs"
    lipidome_tab_title: str = "Lipidomes"
    lipid_tab_title: str = "Lipids"
    change_tab_title: str = "Changes"
    change_tabs_id: str = "changes-tabs"
    lipidome_tab_name: str = "lipidome"
    lipid_tab_name: str = "lipid"
    change_tab_name: str = "change"

    def gen_component(
        self,
        lipidome_grid: dag.AgGrid,
        lipid_grid: dag.AgGrid,
        difference_grid: dag.AgGrid,
        log2fc_grid: dag.AgGrid,
    ) -> dcc.Tabs:
        tabs: dcc.Tabs = dcc.Tabs(
            [
                dcc.Tab(
                    [lipidome_grid],
                    label=self.lipidome_tab_title,
                    value=self.lipidome_tab_name,
                ),
                dcc.Tab(
                    [lipid_grid],
                    label=self.lipid_tab_title,
                    value=self.lipid_tab_name,
                ),
                dcc.Tab(
                    [
                        dcc.Tabs(
                            [
                                dcc.Tab(
                                    [difference_grid],
                                    label="Difference",
                                    value="difference",
                                ),
                                dcc.Tab(
                                    [log2fc_grid],
                                    label="Log2FC",
                                    value="log2fc",
                                ),
                            ],
                            id=self.change_tabs_id,
                            value="difference",
                        ),
                    ],
                    label=self.change_tab_title,
                    value=self.change_tab_name,
                ),
            ],
            value=self.lipidome_tab_name,
            id=self.element_id,
        )

        return tabs


# -- SETTINGS RELATED COMPONENTS ----------------------------------------------


@dataclass(frozen=True)
class SettingsAccordion(ComponentWrapper):
    element_id: str = "settings-accordion"
    data_setup_title: str = "Data Setup"
    data_setup_id: str = "data-setup"
    graph_settings_title: str = "Graph Settings"
    graph_settings_id: str = "graph-settings"
    data_operations_title: str = "Data Operations"
    data_operations_id: str = "data-operations"
    abundance_chart_title: str = "Abundance Chart"
    abundance_chart_id: str = "abundance-chart"
    structure_title: str = "Representative Structure"
    structure_id: str = "structure"
    app_settings_title: str = "App Settings"
    app_settings_id: str = "app-settings"
    manual_title: str = "Manual"
    manual_id: str = "manual"

    def gen_component(
        self,
        upload_setup_button: Component,
        default_dataset_button: Component,
        mode_selection_div: Component,
        dimensionality_selection_div: Component,
        sizemode_selection_div: Component,
        scaling: Component,
        grouping_component: Component,
        change_component: Component,
        set_name_component: Component,
        set_color_component: Component,
        delete_component: Component,
        abundance_graph: Component,
        abundance_graph_fullscreen_button: Component,
        structure_image: Component,
        structure_image_fullscreen_button: Component,
        theme_switch: Component,
        about_button: Component,
        figure_download_settings: Component,
        manual_tour_component: Component,
        session_download: Component,
    ) -> dbc.Accordion:
        settings_accordion: dbc.Accordion = dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        upload_setup_button,
                        html.Br(),
                        default_dataset_button,
                        html.Br(),
                        session_download,
                        html.Br(),
                    ],
                    id=self.data_setup_id,
                    title=self.data_setup_title,
                    item_id=self.data_setup_id,
                ),
                dbc.AccordionItem(
                    [
                        mode_selection_div,
                        dimensionality_selection_div,
                        sizemode_selection_div,
                        scaling,
                        figure_download_settings,
                    ],
                    id=self.graph_settings_id,
                    title=self.graph_settings_title,
                    item_id=self.graph_settings_id,
                ),
                dbc.AccordionItem(
                    [
                        grouping_component,
                        change_component,
                        set_name_component,
                        set_color_component,
                        delete_component,
                    ],
                    id=self.data_operations_id,
                    title=self.data_operations_title,
                    item_id=self.data_operations_id,
                ),
                dbc.AccordionItem(
                    children=html.Div(
                        [abundance_graph_fullscreen_button, abundance_graph],
                        style={"position": "relative"},
                    ),
                    id=self.abundance_chart_id,
                    title=self.abundance_chart_title,
                    item_id=self.abundance_chart_id,
                ),
                dbc.AccordionItem(
                    children=html.Div(
                        [structure_image_fullscreen_button, structure_image],
                        style={"position": "relative"},
                    ),
                    id=self.structure_id,
                    title=self.structure_title,
                    item_id=self.structure_id,
                ),
                dbc.AccordionItem(
                    children=html.Div(
                        [theme_switch, about_button],
                    ),
                    id=self.app_settings_id,
                    title=self.app_settings_title,
                    item_id=self.app_settings_id,
                ),
                dbc.AccordionItem(
                    children=html.Div(
                        [manual_tour_component],
                    ),
                    id=self.manual_id,
                    title=self.manual_title,
                    item_id=self.manual_id,
                ),
            ],
            always_open=True,
            active_item=["data-setup", "graph-settings"],
            id=self.element_id,
        )

        return settings_accordion


# -- DATA SETUP COMPONENTS ----------------------------------------------------


@dataclass(frozen=True)
class DefaultDatasetButton(Button):
    element_id: str = "default-dataset-button"
    text: str = "Load Default Dataset"


@dataclass(frozen=True)
class DefaultDatasetModal(ComponentWrapper):
    element_id: str = "default-dataset-modal"
    selection_dropdown_element_id: str = "default-dataset-selection-dropdown"
    dataset_description_div_element_id: str = "default-dataset-description-div"
    load_dataset_button_element_id: str = "load-dataset-button"
    load_dataset_button_text: str = "Load Dataset"
    size: Literal["sm", "lg", "xl"] = "xl"

    def gen_component(self, dataset_descriptions: dict[str, str]) -> dbc.Modal:
        initial_dataset: str = next(iter(dataset_descriptions.keys()))

        default_dataset_selection_dropdown: dcc.Dropdown = dcc.Dropdown(
            options=[
                {"label": dataset, "value": dataset}
                for dataset in dataset_descriptions.keys()
            ],
            value=initial_dataset,
            id=self.selection_dropdown_element_id,
            clearable=False,
        )

        dataset_description_div: html.Div = html.Div(
            [dataset_descriptions[initial_dataset]],
            id=self.dataset_description_div_element_id,
        )

        load_dataset_button: dbc.Button = dbc.Button(
            self.load_dataset_button_text,
            id=self.load_dataset_button_element_id,
        )

        default_dataset_modal: dbc.Modal = dbc.Modal(
            [
                dbc.ModalBody(
                    [
                        default_dataset_selection_dropdown,
                        dataset_description_div,
                        load_dataset_button,
                    ]
                )
            ],
            is_open=False,
            size=self.size,
            id=self.element_id,
        )

        return default_dataset_modal


@dataclass(frozen=True)
class UploadSetupButton(Button):
    element_id: str = "upload-setup-button"
    text: str = "Dataset Upload Setup"


@dataclass(frozen=True)
class UploadAbundances(UploadComponent):
    element_id: str = "upload-abundances"
    text: str = "Upload Abundances"


@dataclass(frozen=True)
class UploadLipidomeFeatures(UploadComponent):
    element_id: str = "upload-lipidome-features"
    text: str = "Upload Lipidome Features"


@dataclass(frozen=True)
class UploadFAConstraints(UploadComponent):
    element_id: str = "upload-fa-constraints"
    text: str = "Upload FA Constraints"


@dataclass(frozen=True)
class UploadLCBConstraints(UploadComponent):
    element_id: str = "upload-lcb-constraints"
    text: str = "Upload LCB Constraints"


@dataclass(frozen=True)
class UploadInitiateButton(Button):
    element_id: str = "upload-initiate-button"
    text: str = "Upload Data"


@dataclass(frozen=True)
class UploadFailuresGrid(Grid):
    element_id: str = "upload-failures-grid"

    def gen_component(self) -> dag.AgGrid:
        grid: dag.AgGrid = dag.AgGrid(
            id=self.element_id, className="ag-theme-alpine compact"
        )

        return grid


@dataclass(frozen=True)
class UploadModal(ComponentWrapper):
    element_id: str = "upload-modal"
    footer_text_element_id: str = "upload-modal-footer-text"
    title: str = "Upload Lipidome Dataset"
    upload_success_text: str = (
        "Upload successful. The following lipids could not be processed:"
    )
    upload_failure_text: str = (
        "Processing of data lead to an error - formats not recognised."
    )
    size: Literal["sm", "lg", "xl"] = "xl"

    def gen_component(
        self,
        upload_abundances: Component,
        upload_lipidome_features: Component,
        upload_fa_constraints: Component,
        upload_lcb_constraints: Component,
        upload_initiate_button: Component,
        upload_failures_grid: Component,
    ) -> dbc.Modal:
        upload_modal: dbc.Modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(self.title)),
                dbc.ModalBody(
                    [
                        upload_abundances,
                        upload_lipidome_features,
                        upload_fa_constraints,
                        upload_lcb_constraints,
                        upload_initiate_button,
                        html.Hr(),
                        html.Div(id=self.footer_text_element_id),
                        html.Div([upload_failures_grid]),
                    ]
                ),
            ],
            id=self.element_id,
            size=self.size,
            is_open=False,
        )

        return upload_modal


# -- GRAPH SETTINGS COMPONENTS ------------------------------------------------


@dataclass(frozen=True)
class ModeSelection(ComponentWrapper):
    element_id: str = "mode-selection"
    frame_title: str = "Mode"
    option_lipidome_overlay: str = "Lipidome Overlay"
    value_lipidome_overlay: str = "overlay"
    option_pair_difference: str = "Pair Difference"
    value_pair_difference: str = "difference"
    option_pair_log2fc: str = "Pair Log2FC"
    value_pair_log2fc: str = "log2fc"

    def gen_component(self) -> dbc.RadioItems:
        mode_radio_items: dbc.RadioItems = dbc.RadioItems(
            options=[
                {
                    "label": self.option_lipidome_overlay,
                    "value": self.value_lipidome_overlay,
                },
                {
                    "label": self.option_pair_difference,
                    "value": self.value_pair_difference,
                },
                {
                    "label": self.option_pair_log2fc,
                    "value": self.value_pair_log2fc,
                },
            ],
            value="overlay",
            inline=True,
            id=self.element_id,
        )

        return mode_radio_items


@dataclass(frozen=True)
class DimensionalitySelection(ComponentWrapper):
    element_id: str = "dimensionality-selection"
    frame_title: str = "Dimensionality"
    option2d: str = "2D"
    option3d: str = "3D"

    def gen_component(self) -> html.Div:
        dimensionality_radio_items: dbc.RadioItems = dbc.RadioItems(
            options=[
                {"label": self.option2d, "value": 2},
                {"label": self.option3d, "value": 3},
            ],
            value=2,
            inline=True,
            id=self.element_id,
        )

        dimensionality_selection_div: html.Div = html.Div(
            [dimensionality_radio_items]
        )

        return dimensionality_selection_div


@dataclass(frozen=True)
class SizeModeSelection(ComponentWrapper):
    element_id: str = "size-mode-selection"
    frame_title: str = "Size Mode"
    option_area: str = "Area"
    value_area: str = "area"
    option_diameter: str = "Diameter"
    value_diameter: str = "diameter"

    def gen_component(self) -> html.Div:
        sizemode_radio_items: dbc.RadioItems = dbc.RadioItems(
            options=[
                {
                    "label": self.option_area,
                    "value": self.value_area,
                },
                {
                    "label": self.option_diameter,
                    "value": self.value_diameter,
                },
            ],
            value="area",
            inline=True,
            id=self.element_id,
        )

        sizemode_div: html.Div = html.Div([sizemode_radio_items])

        return sizemode_div


@dataclass(frozen=True)
class LinearScaling(ComponentWrapper):
    element_id: str = "linear-scaling"
    factor_element_id: str = "linear-scaling-factor"
    base_element_id: str = "linear-scaling-base"

    heading: str = "Linear scaling"
    factor_heading: str = "Factor"
    base_heading: str = "Base"

    factor_min_area: int = 0
    factor_max_area: int = 150
    factor_value_area: int = 20

    factor_min_diameter: int = 0
    factor_max_diameter: int = 10
    factor_value_diameter: int = 5

    base_min_area: int = 0
    base_max_area: int = 100
    base_value_area: int = 5

    base_min_diameter: int = 0
    base_max_diameter: int = 5
    base_value_diameter: int = 5

    def gen_component(self) -> html.Div:
        factor_slider: dcc.Slider = dcc.Slider(
            id=self.factor_element_id,
            min=self.factor_min_area,
            max=self.factor_max_area,
            value=self.factor_value_area,
        )

        base_slider: dcc.Slider = dcc.Slider(
            id=self.base_element_id,
            min=self.base_min_area,
            max=self.base_max_area,
            value=self.base_value_area,
        )

        div: html.Div = html.Div(
            [
                html.P(self.heading),
                html.P(self.factor_heading),
                factor_slider,
                html.P(self.base_heading),
                base_slider,
            ],
            id=self.element_id,
        )

        return div


@dataclass(frozen=True)
class MinMaxScaling(ComponentWrapper):
    element_id: str = "min-max-scaling"

    text: str = "Marker Size Range:"

    min_area: int = 1
    max_area: int = 10000
    value_area: tuple[int, int] = (50, 5000)

    min_diameter: int = 1
    max_diameter: int = 50
    value_diameter: tuple[int, int] = (5, 30)

    def gen_component(self) -> html.Div:
        range_slider: dcc.RangeSlider = dcc.RangeSlider(
            id=self.element_id,
            min=self.min_area,
            max=self.max_area,
            value=self.value_area,
        )

        div: html.Div = html.Div([html.P(self.text), range_slider])

        return div


@dataclass(frozen=True)
class FigureDownloadSettings(ComponentWrapper):
    element_id: str = "figure download settings"
    frame_title: str = "Figure download settings"

    name_input_id: str = "download-figure-name"
    file_type_dropdown_id: str = "download-figure-file-type"
    height_input_id: str = "download-figure-height"
    width_input_id: str = "download-figure-width"
    scale_factor_input_id: str = "download-figure-scale-factor"

    label_text: str = (
        "To download the figure, click the download icon in "
        "the figure's mode bar."
    )

    def gen_component(self) -> dbc.Container:
        name_input: dcc.Input = dcc.Input(
            id=self.name_input_id,
            value="LipidomeProjectorFigure",
            type="text",
        )
        type_dropdown: dcc.Dropdown = dcc.Dropdown(
            id=self.file_type_dropdown_id,
            options=[
                {"label": "PNG", "value": "png"},
                {"label": "JPEG", "value": "jpeg"},
                {"label": "WebP", "value": "webp"},
                {"label": "SVG", "value": "svg"},
            ],
            value="svg",
        )

        height_input: dcc.Input = dcc.Input(
            id=self.height_input_id,
            value=800,
            type="number",
        )

        width_input: dcc.Input = dcc.Input(
            id=self.width_input_id,
            value=800,
            type="number",
        )

        scale_input: dcc.Input = dcc.Input(
            id=self.scale_factor_input_id,
            value=1.0,
            step=0.1,
            type="number",
        )

        download_label = html.Label(self.label_text)
        ftype_label = html.Label("File Type")
        name_label = html.Label("File Name")
        height_input_label = html.Label("Height")
        width_input_label = html.Label("Width")
        scale_input_label = html.Label("Scale Factor")

        return dbc.Container(
            children=[
                dbc.Row(download_label),
                dbc.Row([dbc.Col(height_input_label), dbc.Col(height_input)]),
                dbc.Row([dbc.Col(width_input_label), dbc.Col(width_input)]),
                dbc.Row([dbc.Col(scale_input_label), dbc.Col(scale_input)]),
                dbc.Row([dbc.Col(name_label), dbc.Col(name_input)]),
                dbc.Row([dbc.Col(ftype_label), dbc.Col(type_dropdown)]),
            ],
            id=self.element_id,
        )


@dataclass(frozen=True)
class Scaling(ComponentWrapper):
    element_id: str = "scaling"
    frame_title: str = "Scaling"

    def gen_component(
        self,
        min_max_scaling: Component,
        linear_scaling: Component,
    ) -> dcc.Tabs:
        tabs: dcc.Tabs = dcc.Tabs(
            [
                dcc.Tab(
                    [min_max_scaling],
                    label="Min-Max",
                    value="min-max",
                ),
                dcc.Tab(
                    [linear_scaling],
                    label="Linear",
                    value="linear",
                ),
            ],
            id=self.element_id,
            value="min-max",
        )

        return tabs


# -- DATA OPERATIONS COMPONENTS -----------------------------------------------


@dataclass(frozen=True)
class GroupingComponent(ComponentWrapper):
    element_id: str = "grouping"
    frame_title: str = "Grouping"

    button_id: str = "create-grouping-button"
    button_text: str = "Create Grouping:"
    dropdown_id: str = "grouping-dropdown"
    mean_text: str = "Mean"
    mean_label: str = "mean"
    std_text: str = "Standard deviation"
    std_label: str = "std"
    name_text: str = "Grouping Name:"
    input_id: str = "grouping-name"
    input_value: str = "Grouping"

    def gen_component(self) -> html.Div:
        grouping_button: dbc.Button = dbc.Button(
            self.button_text, id=self.button_id
        )

        grouping_choice: dcc.Dropdown = dcc.Dropdown(
            options=[
                {"label": self.mean_text, "value": self.mean_label},
                {"label": self.std_text, "value": self.std_label},
            ],
            value="mean",
            id=self.dropdown_id,
        )

        grouping_label: html.Label = html.Label(self.name_text)

        grouping_name_input: dcc.Input = dcc.Input(
            id=self.input_id, value=self.input_value, type="text"
        )

        return html.Div(
            [
                dbc.Row(
                    [dbc.Col(grouping_button), dbc.Col(grouping_choice)],
                ),
                dbc.Row(
                    [dbc.Col(grouping_label), dbc.Col(grouping_name_input)],
                ),
            ]
        )


@dataclass(frozen=True)
class ChangeComponent(ComponentWrapper):
    element_id: str = "change-component"
    frame_title: str = "Pairwise Changes"
    dropdown_id: str = "change-selection-dropdown"
    dropdown_value: str = "difference"
    button_id: str = "compute-change-button"
    button_text: str = "Compute Pairwise Changes"

    def gen_component(self) -> html.Div:
        change_selection_dropdown: dcc.Dropdown = dcc.Dropdown(
            options=[
                {"label": "Difference", "value": "difference"},
                {"label": "Log2FC", "value": "log2fc"},
            ],
            value="difference",
            id=self.dropdown_id,
        )

        change_button: dbc.Button = dbc.Button(
            self.button_text, id=self.button_id
        )

        return html.Div(
            dbc.Row(
                [dbc.Col(change_button), dbc.Col(change_selection_dropdown)]
            )
        )


@dataclass(frozen=True)
class LastDeletedStore(ComponentWrapper):
    element_id: str = "last-deleted-store"

    def gen_component(self) -> dcc.Store:
        store = dcc.Store(id=self.element_id, data={})

        return store


@dataclass(frozen=True)
class DeleteComponent(ComponentWrapper):
    element_id: str = "delete-component"
    frame_title: str = "Delete Lipidomes"

    button_id: str = "delete-button"
    button_text: str = "Delete Selected Lipidomes"

    button_undo_id: str = "undo-delete-button"
    button_undo_text: str = "Undo last deletion"

    def gen_component(self) -> html.Div:
        delete_button: dbc.Button = dbc.Button(
            self.button_text,
            id=self.button_id,
        )

        undo_delete_button: dbc.Button = dbc.Button(
            self.button_undo_text,
            id=self.button_undo_id,
            disabled=True,
        )

        return html.Div(
            dbc.Row([dbc.Col(delete_button), dbc.Col(undo_delete_button)])
        )


@dataclass(frozen=True)
class SetNameComponent(ComponentWrapper):
    element_id: str = "set-name-div"
    frame_title: str = "Set Name"
    button_element_id: str = "set-name-button"
    input_element_id: str = "set-name-input"
    button_text: str = "Set Name of Selected Lipidome: "
    input_value: str = "Lipidome"

    def gen_component(self) -> html.Div:
        set_name_button: dbc.Button = dbc.Button(
            self.button_text, id=self.button_element_id
        )

        set_name_input: dcc.Input = dcc.Input(
            id=self.input_element_id, value=self.input_value, type="text"
        )

        div: html.Div = html.Div(
            dbc.Row([dbc.Col(set_name_button), dbc.Col(set_name_input)]),
            id=self.element_id,
        )

        return div


@dataclass(frozen=True)
class SetColorComponent(ComponentWrapper):
    element_id: str = "color-component"
    frame_title: str = "Color Settings"
    set_color_button_id: str = "set-color-button"
    set_color_button_text: str = "Set Color of Selected Lipidome(s): "
    set_color_picker_id: str = "color-picker"
    set_color_picker_value: str = "#325d88"
    color_scale_button_id: str = "change-color-scale-button"
    color_scale_button_text: str = "Change Color Scale"
    color_scale_dropdown_id: str = "change-color-scale-dropdown"
    color_scale_dropdown_value: str = "Viridis"

    def gen_component(self) -> html.Div:
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(self.gen_set_color_button()),
                        dbc.Col(self.gen_set_color_picker()),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(self.gen_color_scale_button()),
                        dbc.Col(self.gen_color_scale_dropdown()),
                    ]
                ),
            ]
        )

    def gen_set_color_button(self) -> dbc.Button:
        return dbc.Button(
            self.set_color_button_text, id=self.set_color_button_id
        )

    def gen_set_color_picker(self) -> dbc.Input:
        return dbc.Input(
            id=self.set_color_picker_id,
            value=self.set_color_picker_value,
            type="color",
        )

    def gen_color_scale_button(self) -> dbc.Button:
        return dbc.Button(
            self.color_scale_button_text, id=self.color_scale_button_id
        )

    def gen_color_scale_dropdown(self) -> dcc.Dropdown:

        def _generate_color_scale_divs(
            color_scale_name: str, colors: list[str]
        ) -> list[html.Div]:
            colors: list[str] = [
                color if color.startswith("#") else rgb_str_to_hex(color)
                for color in colors
            ]
            color_div_list = [
                html.Div(
                    children=color_scale_name,
                    style={
                        "fontWeight": "bold",
                        "marginRight": "10px",
                        "width": "150px",
                        "textOverflow": "ellipsis",
                        "overflow": "hidden",
                        "whiteSpace": "nowrap",
                    },
                )
            ]
            color_div_list.extend(
                [
                    html.Div(
                        style={
                            "backgroundColor": color,
                            "height": "20px",
                            "width": "20px",
                        }
                    )
                    for color in colors
                ]
            )
            return color_div_list

        def _get_color_scales():
            color_scale_dict = px.colors.qualitative.swatches().to_dict()
            color_scales = []

            for trace in color_scale_dict["data"]:
                colors = trace.get("marker").get("color")
                color_scale_name = trace.get("y")[0]
                color_scales.append(
                    {
                        "label": _generate_color_scale_divs(
                            color_scale_name, colors
                        ),
                        "value": color_scale_name,
                    }
                )

            return color_scales

        return dcc.Dropdown(
            id=self.color_scale_dropdown_id,
            options=_get_color_scales(),
            value=self.color_scale_dropdown_value,
        )


# -- APP SETTINGS COMPONENTS -----------------------------------------------


@dataclass(frozen=True)
class ThemeSwitch(ComponentWrapper):
    element_id: str = "theme-switch"
    switch_id: str = "theme-switch-switch"
    store_id: str = "theme-switch-store"
    theme_name: str = "theme-name-div"
    frame_title: str = "App Theme"
    dark_theme_name: str = "SLATE"
    light_theme_name: str = "SANDSTONE"

    themes = [
        "/assets/" + dark_theme_name + ".css",
        "/assets/" + light_theme_name + ".css",
    ]

    """This is an altered copy of the original ThemeSwitchAIO component from dash-bootstrap-templates package."""

    switch_props = {"value": False, "className": "d-inline-block ms-1"}

    load_figure_template(light_theme_name)

    clientside_callback(
        """
        function toggle(theme_switch, url) {
          var themeLink = theme_switch ? url[0] : url[1];
          var oldThemeLink = theme_switch ? url[1]: url[0];
          var testString = "link[rel='stylesheet'][href*='" + oldThemeLink + "'],"
            testString += "link[rel='stylesheet'][href*='" + themeLink + "'],"
            testString += "link[rel='stylesheet'][data-href*='" + oldThemeLink + "'],"
            testString += "link[rel='stylesheet'][data-href*='" + themeLink + "']"

          var stylesheets = document.querySelectorAll(testString);
          
          setTimeout(function() {
            if (stylesheets) {
                for (let i = 0; i < stylesheets.length; i++) {
                    if (!stylesheets[i].getAttribute('data-href')) {
                        stylesheets[i].setAttribute('data-href', '')
                    }
                    if (stylesheets[i].href.includes(themeLink) || stylesheets[i].getAttribute('data-href').includes(themeLink)) {
                        if (stylesheets[i]['data-href']) {
                            stylesheets[i].href = stylesheets[i]['data-href'];
                        } else {
                            stylesheets[i].href = themeLink;
                        }
                        stylesheets[i].setAttribute('data-href', '')
                    }
                    else if (stylesheets[i].href.includes(oldThemeLink) || stylesheets[i].getAttribute('data-href').includes(oldThemeLink)) {
                        setTimeout(function () {
                        if (stylesheets[i]['href']) {
                            stylesheets[i].setAttribute('data-href', stylesheets[i]['href']);
                        } else {
                            stylesheets[i].setAttribute('data-href', oldThemeLink)
                        }
                        stylesheets[i]['href'] = ''
                        }, 100)
                    }
                };
            }
            var stylesheet = document.querySelectorAll('link[rel="stylesheet"][href*="'+ themeLink + '"]')
            if (stylesheet.length == 0) {
                var newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = themeLink;
                newLink.setAttribute('data-href', '');
                document.head.appendChild(newLink);
            }
          }, 100); 
          
          /* reload custom.css after theme has been switched to enable custom changes to theme vars */
          setTimeout(function() {  
              var reloadCustom = document.createElement('link');
              reloadCustom.rel = 'stylesheet';
              reloadCustom.href = "/assets/custom.css";
              reloadCustom.setAttribute('data-href', '');
              document.head.appendChild(reloadCustom);
            }, 150);
          
          var themeName = themeLink.split('/').pop().replace('.css', '').toLowerCase();
          return themeName;
        }
        """,
        Output(theme_name, "children"),
        Input(switch_id, "value"),
        Input(store_id, "data"),
    )

    def gen_component(self) -> html.Div:
        return html.Div(
            children=[
                html.Span(
                    [
                        html.Span("\u2600", style={"fontSize": "150%"}),  # sun
                        dbc.Switch(id=self.switch_id, **self.switch_props),
                        html.Span(
                            "\u263D", style={"fontSize": "150%"}
                        ),  # moon
                    ],
                ),
                dcc.Store(id=self.store_id, data=self.themes),
                html.Div(id=self.theme_name, hidden=True),
            ],
            id=self.element_id,
        )


@dataclass(frozen=True)
class AboutButton(Button):
    element_id: str = "about-button"
    text: str = "About"


# TODO: Update version display.
@dataclass(frozen=True)
class AboutModal(ComponentWrapper):
    element_id: str = "about-modal"
    version = 0.1  # TODO: get version

    def gen_component(self, *args, **kwargs) -> dbc.Modal:
        about_modal_content = html.Div(
            [
                html.H6(
                    f"Lipid Projector version:{self.version} (build: {""})"
                ),
                html.Hr(),
                html.H4(html.B("Developers")),
                html.P(
                    html.Table(
                        [
                            html.Tr(
                                [
                                    html.Td(html.B("Lukas Müller")),
                                    html.Td(
                                        html.B(
                                            html.A(
                                                "FZ Borstel",
                                                href="https://www.fz-borstel.de/index.php/de/"
                                                "sitemap/programmbereich-infektionen/"
                                                "bioanalytische-chemie-dr-dominik-schwudke/"
                                                "mitarbeiter-innen#innercontent",
                                            )
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td(html.B("Timur Olzhabeav")),
                                    html.Td(
                                        html.B(
                                            html.A(
                                                "ZBH Hamburg",
                                                href="https://www.zbh.uni-hamburg.de/en/personen/"
                                                "bm/tolzhabaev.html",
                                            )
                                        ),
                                    ),
                                ]
                            ),
                        ],
                        className="table-about",
                    )
                ),
                html.H5("Editorial & Thanks to"),
                html.P(
                    html.Table(
                        [
                            html.Tr(
                                [
                                    html.Td("PD Dr.Dominik Schwudke"),
                                    html.Td(
                                        html.A(
                                            "FZ Borstel",
                                            href="https://www.fz-borstel.de/index.php/de/"
                                            "sitemap/programmbereich-infektionen/"
                                            "bioanalytische-chemie-dr-dominik-schwudke/"
                                            "mission",
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Prof. Dr. Andrew Torda"),
                                    html.Td(
                                        html.A(
                                            "ZBH Hamburg",
                                            href="https://www.zbh.uni-hamburg.de/personen/bm/"
                                            "atorda.html",
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Daniel Krause"),
                                    html.Td(
                                        html.A(
                                            "FZ Borstel",
                                            href="https://www.fz-borstel.de/index.php/de/"
                                            "sitemap/programmbereich-infektionen/"
                                            "bioanalytische-chemie-dr-dominik-schwudke/"
                                            "mitarbeiter-innen#innercontent",
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td(
                                        html.A(
                                            "LIFS tools community",
                                            href="https://lifs-tools.org/",
                                        )
                                    )
                                ]
                            ),
                        ],
                        className="table-about",
                    )
                ),
                html.H5("References"),
                html.P(
                    html.Table(
                        [
                            html.Tr(
                                [
                                    html.Td("Drosophila lipidome data"),
                                    html.Td(
                                        html.A(
                                            "Carvalho et al.(2012)",
                                            href="https://pubmed.ncbi.nlm.nih.gov/22864382/",
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Yeast lipidome data"),
                                    html.Td(
                                        html.A(
                                            "Ejsing et al.(2009)",
                                            href="https://pubmed.ncbi.nlm.nih.gov/19174513/",
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("SwissLipids knowledge base"),
                                    html.Td(
                                        html.A(
                                            "Aimo et al.(2015)",
                                            href="https://www.ncbi.nlm.nih.gov/pmc/articles/"
                                            "PMC4547616/",
                                        ),
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td(
                                        "LIPIDMAPS\u00AE StructureDatabase"
                                    ),
                                    html.Td(
                                        html.A(
                                            "Sud et al.(2007)",
                                            href="https://pubmed.ncbi.nlm.nih.gov/17098933/",
                                        )
                                    ),
                                ]
                            ),
                        ],
                        className="table-about",
                    )
                ),
            ]
        )

        about_modal = dbc.Modal(
            [
                dbc.ModalHeader(html.H4("About Lipidome Projector")),
                dbc.ModalBody(about_modal_content),
            ],
            id=self.element_id,
            size="lg",
            is_open=False,
        )

        return about_modal

    @staticmethod
    def _get_last_commit_date() -> str:
        try:
            git_path: Path = Path(Path.cwd(), ".git")
            ref_path: Path = Path(git_path / "refs" / "heads" / "main")
            commit_hash: str = ref_path.read_text().strip()
            commit_path: Path = Path(
                git_path / "objects" / commit_hash[:2] / commit_hash[2:]
            )
            commit_data: bytes = commit_path.read_bytes()
            decompressed_data: bytes = decompress(commit_data)
            commit_lines: list[str] = decompressed_data.decode(
                "utf-8", errors="ignore"
            ).split("\n")
            for line in commit_lines:
                if line.startswith("committer "):
                    timestamp: str = line.split(" ")[3]
                    commit_date: datetime = datetime.fromtimestamp(
                        int(timestamp)
                    )
                    formatted_date: str = commit_date.strftime("%d-%m-%Y")
                    return formatted_date
        except Exception as e:
            print(e)
            return "-"


# -- MANUAL COMPONENTS -----------------------------------------------


@dataclass(frozen=True)
class ManualTourComponent(ComponentWrapper):
    element_id: str = "manual-tour"
    frame_title: str = "Choose a manual tour"

    button_id: str = "start-tour-button"
    button_text: str = "Start Tour"
    dropdown_id: str = "choose-tour-dropdown"

    def gen_component(self, tours) -> html.Div:
        start_tour_button: dcc.Loading = dcc.Loading(
            children=dbc.Button(
                children=self.button_text,
                id=self.button_id,
            ),
            overlay_style={"visibility": "visible", "display": "inline-block"},
            parent_style={"display": "inline-block"},
        )

        dropdown_options: list[dict[str, str]] = [
            {"label": tour, "value": tour} for tour in tours.keys()
        ]
        tour_dropdown: dcc.Dropdown = dcc.Dropdown(
            id=self.dropdown_id,
            options=dropdown_options,
            value=dropdown_options[0]["value"],
            clearable=False,
        )
        return html.Div(
            children=dbc.Container(
                [dbc.Row([dbc.Col(start_tour_button), dbc.Col(tour_dropdown)])]
            ),
            id=self.element_id,
        )


@dataclass(frozen=True)
class TourStepAction:
    target_id: str
    target_prop: str
    value: Any


@dataclass(frozen=True)
class TourStepImage:
    src: str
    description: str | html.Div = ""

    def get_component(self) -> html.Div:
        image_path: Path = (
            files(
                "lipidome_projector.assets"
            ).joinpath(
                "manual_tour"
            ).joinpath(
                self.src
            )
        )
        if image_path.exists():
            suffix: str = image_path.suffix
            if suffix not in [".png", ".jpg", ".jpeg", ".gif"]:
                raise ValueError(
                    f"Tour image {image_path} has an invalid suffix {suffix}"
                )
            image: str = b64encode(open(image_path, "rb").read()).decode(
                "ascii"
            )
        else:
            raise FileNotFoundError(f"Tour image {image_path} not found")
        return html.Div(
            [
                html.Img(
                    src=f"data:image/{suffix};base64,{image}",
                    id=image_path.name,
                ),
                (
                    html.Div(
                        self.description, className="tour-image-description"
                    )
                    if self.description
                    else html.Div()
                ),
            ],
            style={"position": "relative", "width": "100%"},
        )


@dataclass(frozen=True)
class TourStep:
    description: str | html.Div
    target: str
    action: TourStepAction | None = field(default=None)
    image: TourStepImage | None = field(default=None)
    placement: str = "auto"


@dataclass(frozen=True)
class TourComponent(ComponentWrapper):
    manual_tour_component: ManualTourComponent = field(default=None)
    tour_name: str = field(default=None)
    next_: Self = field(default=None)
    description: str = field(default=None)
    target_id: str = field(default=None)
    popover_id: str = field(init=False)
    next_button_id: str = field(init=False)
    close_button_id: str = field(init=False)
    action: TourStepAction | None = field(default=None)
    image: TourStepImage | None = field(default=None)
    placement: str = "auto"

    def set_next(self, next_component: Self) -> None:
        object.__setattr__(self, "next_", next_component)

    def gen_component(self) -> dbc.Popover:
        popover = dbc.Popover(
            id=self.popover_id,
            body=True,
            placement=self.placement,
            children=html.Div(
                [
                    dbc.Row([html.Label(self.description)]),
                    (
                        dbc.Row([self.image.get_component()])
                        if self.image is not None
                        else html.Div()
                    ),
                    html.Div(
                        children=html.Div(
                            [
                                dbc.Button(
                                    "»",
                                    id=self.next_button_id,
                                    className="tour-button fwd-tour",
                                ),
                                dbc.Button(
                                    "✖",
                                    id=self.close_button_id,
                                    className="tour-button close-tour",
                                ),
                            ],
                            className="tour-button-container",
                        ),
                        id=self.element_id,
                    ),
                ]
            ),
        )
        return popover

    def __post_init__(self) -> None:
        object.__setattr__(self, "popover_id", f"popover_{self.element_id}")
        object.__setattr__(
            self, "next_button_id", f"popover_next_{self.element_id}"
        )
        object.__setattr__(
            self, "close_button_id", f"popover_close_{self.element_id}"
        )

    def register_callback(self) -> None:
        @callback(
            Output(
                self.manual_tour_component.button_id,
                "className",
                allow_duplicate=True,
            ),
            Output(
                self.manual_tour_component.button_id,
                "disabled",
                allow_duplicate=True,
            ),
            Output(
                self.manual_tour_component.dropdown_id,
                "disabled",
                allow_duplicate=True,
            ),
            Output(self.next_.popover_id, "is_open", allow_duplicate=True),
            Output(self.popover_id, "is_open", allow_duplicate=True),
            Output(self.next_.popover_id, "className", allow_duplicate=True),
            Input(self.next_button_id, "n_clicks"),
            Input(self.close_button_id, "n_clicks"),
            Input(self.manual_tour_component.button_id, "n_clicks"),
            State(self.popover_id, "is_open"),
            prevent_initial_call=True,
        )
        def toggle_popover(
            next_button: int | None,
            close_button: int | None,
            start_tour: int | None,
            is_open: bool,
        ) -> tuple[
            str | NoUpdate, bool | NoUpdate, bool | NoUpdate, bool, bool, str
        ]:
            next_popover_width_class = (
                "popover"
                if self.next_.image is None
                else "popover popover-max-width"
            )
            if self.close_button_id in ctx.triggered_id:
                return (
                    no_update,
                    False,
                    False,
                    False,
                    False,
                    next_popover_width_class,
                )
            elif self.next_button_id in ctx.triggered_id:
                return (
                    no_update,
                    no_update,
                    no_update,
                    True,
                    False,
                    next_popover_width_class,
                )
            elif (
                is_open
                and self.manual_tour_component.button_id in ctx.triggered_id
            ):
                return (
                    "loading",
                    True,
                    True,
                    no_update,
                    False,
                    next_popover_width_class,
                )
            raise PreventUpdate

        clientside_callback(
            ClientsideFunction(
                namespace="clientside",
                function_name="tour_listens_to_keys",
            ),
            Output(self.next_button_id, "n_clicks"),
            Input(self.popover_id, "is_open"),
            State(self.next_button_id, "id"),
            State(self.close_button_id, "id"),
            prevent_initial_call=True,
        )

        if self.action is not None:

            @callback(
                Output(
                    self.action.target_id,
                    self.action.target_prop,
                    allow_duplicate=True,
                ),
                Input(self.popover_id, "is_open"),
                prevent_initial_call=True,
            )
            def action(is_open: bool) -> Any:
                if is_open:
                    return self.action.value
                else:
                    raise PreventUpdate

            @callback(
                Output(self.popover_id, "target", allow_duplicate=True),
                Input(self.next_button_id, "n_clicks"),
                prevent_initial_call=True,
            )
            def unset_target(
                n_clicks: int | None,
            ) -> bool:
                # necessary because popover lose target on a closed modal leaves the DOM:
                # https://community.plotly.com/t/dbc-popover-loses-target-when-target-leaves-dom-and-cannot-be-retargeted/84863
                return False

    def set_target(self) -> None:
        @callback(
            Output(self.next_.popover_id, "target", allow_duplicate=True),
            Input(self.popover_id, "is_open"),
            prevent_initial_call=True,
        )
        def set_targets(is_open: bool) -> str:
            if is_open:
                return self.next_.target_id
            else:
                raise PreventUpdate


@dataclass(frozen=True)
class TourComponentStart(TourComponent):
    element_id: str = field(default=None)
    description: str = field(default=None)
    target_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "element_id", f"start-tour-step_{self.tour_name}"
        )
        object.__setattr__(
            self, "target_id", self.manual_tour_component.button_id
        )
        object.__setattr__(self, "popover_id", f"popover_{self.element_id}")
        object.__setattr__(
            self, "next_button_id", f"popover_next_{self.element_id}"
        )
        object.__setattr__(
            self, "close_button_id", f"popover_close_{self.element_id}"
        )
        object.__setattr__(
            self,
            "description",
            f"Click '»' to start '{self.tour_name}' tour. You can also navigate through the tour using the right arrow key and close it with the escape key.",
        )
        clientside_callback(
            ClientsideFunction(
                namespace="clientside", function_name="updateButtonColor"
            ),
            Output(self.element_id, "children", allow_duplicate=True),
            Input(self.manual_tour_component.button_id, "n_clicks"),
            State(self.manual_tour_component.button_id, "id"),
            prevent_initial_call=True,
        )

    def register_callback(self) -> None:

        @callback(
            Output(
                self.manual_tour_component.button_id,
                "disabled",
                allow_duplicate=True,
            ),
            Output(
                self.manual_tour_component.dropdown_id,
                "disabled",
                allow_duplicate=True,
            ),
            Output(self.next_.popover_id, "is_open", allow_duplicate=True),
            Output(self.popover_id, "is_open", allow_duplicate=True),
            Input(self.manual_tour_component.button_id, "n_clicks"),
            Input(self.next_button_id, "n_clicks"),
            Input(self.close_button_id, "n_clicks"),
            State(self.manual_tour_component.dropdown_id, "value"),
            prevent_initial_call=True,
        )
        def toggle_popover(
            start_tour: int | None,
            next_button: int | None,
            close_button: int | None,
            chosen_tour: str,
        ) -> tuple[bool | NoUpdate, bool | NoUpdate, bool, bool]:
            if chosen_tour == self.tour_name:
                if self.close_button_id in ctx.triggered_id:
                    return False, False, False, False
                elif self.manual_tour_component.button_id in ctx.triggered_id:
                    return True, True, False, True
                elif self.next_button_id in ctx.triggered_id:
                    return no_update, no_update, True, False
            else:
                raise PreventUpdate

        clientside_callback(
            ClientsideFunction(
                namespace="clientside",
                function_name="tour_listens_to_keys",
            ),
            Output(self.next_button_id, "n_clicks"),
            Input(self.popover_id, "is_open"),
            State(self.next_button_id, "id"),
            State(self.close_button_id, "id"),
            prevent_initial_call=True,
        )

    def set_target(self):
        @callback(
            Output(self.popover_id, "target"),
            Output(self.next_.popover_id, "target"),
            Input(self.manual_tour_component.button_id, "n_clicks"),
            State(self.popover_id, "target"),
            prevent_initial_call=True,
        )
        def set_target(start_tour: int | None, target: str) -> tuple[str, str]:
            return (
                self.manual_tour_component.button_id,
                self.next_.target_id,
            )


@dataclass(frozen=True)
class TourComponentEnd(TourComponent):
    settings_accordion: SettingsAccordion = field(default=None)
    element_id: str = field(default=None)
    description: str = field(default=None)
    target_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "element_id", f"end-tour-step_{self.tour_name}"
        )
        object.__setattr__(
            self, "target_id", self.settings_accordion.manual_id
        )
        object.__setattr__(self, "popover_id", f"popover_{self.element_id}")
        object.__setattr__(
            self, "next_button_id", f"popover_next_{self.element_id}"
        )
        object.__setattr__(
            self, "close_button_id", f"popover_close_{self.element_id}"
        )
        object.__setattr__(
            self, "description", f"Click '✖' to end '{self.tour_name}' tour."
        )

    def register_callback(self) -> None:
        @callback(
            Output(self.next_button_id, "disabled"),
            Input(self.next_button_id, "id"),
        )
        def disable_next_button(id_: str) -> bool:
            return True

        @callback(
            Output(
                self.manual_tour_component.button_id,
                "disabled",
                allow_duplicate=True,
            ),
            Output(
                self.manual_tour_component.dropdown_id,
                "disabled",
                allow_duplicate=True,
            ),
            Output(self.popover_id, "is_open", allow_duplicate=True),
            Input(self.close_button_id, "n_clicks"),
            prevent_initial_call=True,
        )
        def toggle_popover(
            close_button: int | None,
        ) -> tuple[bool, bool, bool]:
            return False, False, False

        clientside_callback(
            ClientsideFunction(
                namespace="clientside",
                function_name="tour_listens_to_keys",
            ),
            Output(self.next_button_id, "n_clicks"),
            Input(self.popover_id, "is_open"),
            State(self.next_button_id, "id"),
            State(self.close_button_id, "id"),
            prevent_initial_call=True,
        )

    def set_target(self) -> None:
        pass


@dataclass(frozen=True)
class TourHandler:
    manual_tour_component: ManualTourComponent
    settings_accordion: SettingsAccordion

    def gen_tour_components(
        self, tours: dict[str, list[TourStep]]
    ) -> list[Component]:

        tours_steps: list[Component] = []

        for tour_name, tour_list in tours.items():

            tour_steps: list[TourComponent] = [self._get_tour_start(tour_name)]

            for step_index, step in enumerate(tour_list):
                tour_steps.append(
                    self._get_tour_step(tour_name, step, step_index)
                )

            tour_steps.append(self._get_tour_end(tour_name))

            self._set_next(tour_steps)

            self._register_callbacks(tour_steps)

            self._set_target(tour_steps)

            tours_steps.extend(self._get_components(tour_steps))

        return tours_steps

    def _get_tour_step(
        self, tour_name: str, step: TourStep, step_index: int
    ) -> TourComponent:

        return TourComponent(
            element_id=f"target:{step.target}_tour-step:{step_index}_tour:{tour_name}",
            tour_name=tour_name,
            target_id=step.target,
            description=step.description,
            manual_tour_component=self.manual_tour_component,
            action=step.action,
            image=step.image,
            placement=step.placement,
        )

    def _get_tour_start(self, tour_name: str) -> TourComponent:
        return TourComponentStart(
            manual_tour_component=self.manual_tour_component,
            tour_name=tour_name,
        )

    def _get_tour_end(self, tour_name: str) -> TourComponent:
        return TourComponentEnd(
            settings_accordion=self.settings_accordion,
            tour_name=tour_name,
            manual_tour_component=self.manual_tour_component,
        )

    @staticmethod
    def _get_components(tour_steps: list[TourComponent]) -> list[Component]:
        return [tour_step.get_component() for tour_step in tour_steps]

    @staticmethod
    def _set_next(tour_steps: list[TourComponent]) -> None:
        tour_steps[0].set_next(tour_steps[1])

        for i in range(1, len(tour_steps)):
            if i < len(tour_steps) - 1 and tour_steps[i + 1] is not None:
                tour_steps[i].set_next(tour_steps[i + 1])

    @staticmethod
    def _register_callbacks(tour_steps: list[TourComponent]) -> None:
        for tour_step in tour_steps:
            tour_step.register_callback()

    @staticmethod
    def _set_target(tour_steps: list[TourComponent]) -> None:
        for tour_step in tour_steps:
            tour_step.set_target()


@dataclass(frozen=True)
class SessionDownloadComponent(ComponentWrapper):
    element_id: str = "session-download-component"
    button_id: str = "session-download-button"
    upload_id: str = "session-upload"

    def gen_component(self) -> html.Div:
        download_button: dbc.Button = dbc.Button(
            "Download Session State", id=self.button_id
        )

        upload_style: dict[str, str] = {
            "width": "50%",
            "height": "40px",
            "lineHeight": "20px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
        }

        return html.Div(
            [
                download_button,
                html.Br(),
                dcc.Upload(
                    id=self.upload_id,
                    children=["Upload Session State"],
                    style=upload_style,
                ),
                dcc.Download(id=self.element_id),
            ],
        )
