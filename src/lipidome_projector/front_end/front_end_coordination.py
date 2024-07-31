"""Module concerning the coordination of front-end components."""

import base64
import logging

from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

from dash import html
from dash.development.base_component import Component

import lipidome_projector.front_end.front_end_components as fec

from lipidome_projector.lipidome.col_names import ColNames


logger: logging.Logger = logging.getLogger(__name__)

# TODO: Extract tour handling.
# TODO: Refactor to a more nested composition.

@dataclass(frozen=True)
class FrontEnd:

    split_vertical: fec.SplitVertical = field(
        default_factory=fec.SplitVertical
    )

    split_horizontal: fec.SplitHorizontal = field(
        default_factory=fec.SplitHorizontal
    )

    fullscreen_size_store: fec.FullScreenSizeStore = field(
        default_factory=fec.FullScreenSizeStore
    )

    last_deleted_store: fec.LastDeletedStore = field(
        default_factory=fec.LastDeletedStore
    )

    test_warning: fec.TestWarning = field(default_factory=fec.TestWarning)

    problem_modal: fec.ProblemModal = field(default_factory=fec.ProblemModal)

    lipidome_graph: fec.LipidomeGraph = field(
        default_factory=fec.LipidomeGraph
    )

    lipidome_graph_fullscreen_button: fec.LipidomeGraphFullscreenButton = (
        field(default_factory=fec.LipidomeGraphFullscreenButton)
    )

    lipidome_graph_fullscreen_modal: fec.FullScreenModalLipidomeGraph = field(
        default_factory=fec.FullScreenModalLipidomeGraph
    )

    abundance_graph: fec.AbundanceGraph = field(
        default_factory=fec.AbundanceGraph
    )

    abundance_graph_fullscreen_button: fec.AbundanceGraphFullscreenButton = (
        field(default_factory=fec.AbundanceGraphFullscreenButton)
    )

    abundance_graph_fullscreen_modal: fec.FullScreenModalAbundanceGraph = (
        field(default_factory=fec.FullScreenModalAbundanceGraph)
    )

    structure_image: fec.StructureImage = field(
        default_factory=fec.StructureImage
    )

    structure_image_fullscreen_button: fec.StructureImageFullscreenButton = (
        field(default_factory=fec.StructureImageFullscreenButton)
    )

    structure_image_fullscreen_modal: fec.FullScreenModalStructureImage = (
        field(default_factory=fec.FullScreenModalStructureImage)
    )

    theme_switch: fec.ThemeSwitch = field(default_factory=fec.ThemeSwitch)

    about_button: fec.AboutButton = field(default_factory=fec.AboutButton)

    about_modal: fec.AboutModal = field(default_factory=fec.AboutModal)

    lipidome_grid: fec.LipidomeGrid = field(default_factory=fec.LipidomeGrid)

    lipid_grid: fec.LipidGrid = field(default_factory=fec.LipidGrid)

    difference_grid: fec.DifferenceGrid = field(
        default_factory=fec.DifferenceGrid
    )

    log2fc_grid: fec.Log2FCGrid = field(default_factory=fec.Log2FCGrid)

    grid_tabs: fec.GridTabs = field(default_factory=fec.GridTabs)

    settings_accordion: fec.SettingsAccordion = field(
        default_factory=fec.SettingsAccordion
    )

    default_dataset_button: fec.DefaultDatasetButton = field(
        default_factory=fec.DefaultDatasetButton
    )

    default_dataset_modal: fec.DefaultDatasetModal = field(
        default_factory=fec.DefaultDatasetModal
    )

    upload_setup_button: fec.UploadSetupButton = field(
        default_factory=fec.UploadSetupButton
    )

    upload_abundances: fec.UploadComponent = field(
        default_factory=fec.UploadAbundances
    )

    upload_lipidome_features: fec.UploadComponent = field(
        default_factory=fec.UploadLipidomeFeatures
    )

    upload_fa_constraints: fec.UploadComponent = field(
        default_factory=fec.UploadFAConstraints
    )

    upload_lcb_constraints: fec.UploadComponent = field(
        default_factory=fec.UploadLCBConstraints
    )

    upload_initiate_button: fec.UploadInitiateButton = field(
        default_factory=fec.UploadInitiateButton
    )

    upload_failures_grid: fec.UploadFailuresGrid = field(
        default_factory=fec.UploadFailuresGrid
    )

    upload_modal: fec.UploadModal = field(default_factory=fec.UploadModal)

    grouping_component: fec.GroupingComponent = field(
        default_factory=fec.GroupingComponent
    )

    change_component: fec.ChangeComponent = field(
        default_factory=fec.ChangeComponent
    )

    set_color_component: fec.SetColorComponent = field(
        default_factory=fec.SetColorComponent
    )

    set_name_component: fec.SetNameComponent = field(
        default_factory=fec.SetNameComponent
    )

    delete_component: fec.DeleteComponent = field(
        default_factory=fec.DeleteComponent
    )

    mode_selection: fec.ModeSelection = field(
        default_factory=fec.ModeSelection
    )

    dimensionality_selection: fec.DimensionalitySelection = field(
        default_factory=fec.DimensionalitySelection
    )

    sizemode_selection: fec.SizeModeSelection = field(
        default_factory=fec.SizeModeSelection
    )

    linear_scaling: fec.LinearScaling = field(
        default_factory=fec.LinearScaling
    )

    min_max_scaling: fec.MinMaxScaling = field(
        default_factory=fec.MinMaxScaling
    )

    scaling: fec.Scaling = field(default_factory=fec.Scaling)

    figure_download_settings: fec.FigureDownloadSettings = field(
        default_factory=fec.FigureDownloadSettings
    )

    manual_tour_component: fec.ManualTourComponent = field(
        default_factory=fec.ManualTourComponent
    )

    tour_handler: fec.TourHandler = field(init=False)

    def __post_init__(self):
        object.__setattr__(
            self,
            "tour_handler",
            fec.TourHandler(
                self.manual_tour_component,
                self.settings_accordion,
            ),
        )

    def _get_tours(self) -> dict[str, list[fec.TourStep]]:
        tours: dict[str, list[fec.TourStep]] = {
            "Load data": [
                fec.TourStep(
                    target=self.settings_accordion.data_setup_id,
                    description=f"To load data in Lipidome Projector, navigate to '{self.settings_accordion.data_setup_title}'.",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.data_setup_id,
                    ),
                ),
                fec.TourStep(
                    target=self.default_dataset_button.element_id,
                    description="Click here to load any preset dataset.",
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_button.element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.default_dataset_modal.selection_dropdown_element_id,
                    description=html.Div(
                        [
                            html.Div(
                                "Choose a dataset from the list. E.g. the Drosophila dataset"
                            ),
                            html.I("(CARVALHO, Maria, et al. 2012)."),
                        ]
                    ),
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_modal.selection_dropdown_element_id,
                        target_prop="value",
                        value="Drosophila",
                    ),
                ),
                fec.TourStep(
                    target=self.default_dataset_modal.load_dataset_button_element_id,
                    description="Click here to load the selected dataset.",
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_modal.load_dataset_button_element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="The Drosophila dataset is now visualized.",
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_modal.element_id,
                        target_prop="is_open",
                        value=False,
                    ),
                ),
                fec.TourStep(
                    target=self.upload_setup_button.element_id,
                    description="Alternatively, you can load a dataset yourself.",
                    action=fec.TourStepAction(
                        target_id=self.upload_setup_button.element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.upload_abundances.element_id,
                    description="First a file with abundances must be uploaded.",
                    action=fec.TourStepAction(
                        target_id=self.upload_abundances.element_id,
                        target_prop="contents",
                        value=f"data:text/csv;base64,{base64.b64encode(
                            files("lipidome_projector.data").joinpath(
                                "datasets/yeast_abundances.csv"
                            ).read_bytes()
                        ).decode('ascii')}",
                    ),
                    image=fec.TourStepImage(
                        description="Upload the abundances file.",
                        src="abundances_upload.gif",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_abundances.element_id,
                    description="The abundance file should look like this:",
                    image=fec.TourStepImage(
                        description=html.Div(
                            [
                                html.Li(
                                    "A column 'LIPIDOMES', listing all lipidomes"
                                ),
                                html.Li(
                                    "A column for each lipid, found in any of the lipidomes. The lipid columns contain the abundance of a lipid in a lipidome."
                                ),
                            ]
                        ),
                        src="abundances_screenshot.png",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_lipidome_features.element_id,
                    description="Next, a file with lipidome features must be uploaded.",
                    action=fec.TourStepAction(
                        target_id=self.upload_lipidome_features.element_id,
                        target_prop="contents",
                        # value=f"data:text/csv;base64,{base64.b64encode(open(Path.cwd() / 'data' / 'datasets' / 'yeast_features.csv', 'rb').read()).decode('ascii')}",
                        value=f"data:text/csv;base64,{base64.b64encode(
                            files("lipidome_projector.data").joinpath(
                                "datasets/yeast_features.csv"
                            ).read_bytes()
                        ).decode('ascii')}",
                    ),
                    image=fec.TourStepImage(
                        description="Upload the lipidome features file.",
                        src="features_upload.gif",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_lipidome_features.element_id,
                    description="The lipidome features file should look like this:",
                    image=fec.TourStepImage(
                        description=html.Div(
                            [
                                html.Li(
                                    "A column 'LIPIDOMES', listing all lipidomes, matching those in the abundances file."
                                ),
                                html.Li(
                                    "A column for each feature, found in any of the lipidomes."
                                ),
                            ]
                        ),
                        src="features_screenshot.png",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_fa_constraints.element_id,
                    description="Then, two constraint failes need to be uploaded. The first concerns the fatty acyls.",
                    action=fec.TourStepAction(
                        target_id=self.upload_fa_constraints.element_id,
                        target_prop="contents",
                        value=f"data:text/csv;base64,{base64.b64encode(
                            files("lipidome_projector.data").joinpath(
                                "datasets/yeast_fa.csv"
                            ).read_bytes()
                        ).decode('ascii')}",
                    ),
                    image=fec.TourStepImage(
                        description="Upload the fatty acid constraints file.",
                        src="fa_upload.gif",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_fa_constraints.element_id,
                    description="The fatty acid constraints file should look like this:",
                    image=fec.TourStepImage(
                        description=html.Div(
                            [
                                html.Li(
                                    "A colum that lists a fatty acyl profile that is present in the lipidome."
                                ),
                            ]
                        ),
                        src="fa_screenshot.png",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_lcb_constraints.element_id,
                    description="The second constraints the long chain bases.",
                    action=fec.TourStepAction(
                        target_id=self.upload_lcb_constraints.element_id,
                        target_prop="contents",
                        value=f"data:text/csv;base64,{base64.b64encode(
                            files("lipidome_projector.data").joinpath(
                                "datasets/yeast_lcb.csv"
                            ).read_bytes()
                        ).decode('ascii')}",
                    ),
                    image=fec.TourStepImage(
                        description="Upload the long chain base constraints file.",
                        src="lcb_upload.gif",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_lcb_constraints.element_id,
                    description="The long chain base constraints file should look like this:",
                    image=fec.TourStepImage(
                        description=html.Div(
                            [
                                html.Li(
                                    "A column that lists a long chain base profile that is present in the lipidome."
                                ),
                            ]
                        ),
                        src="lcb_screenshot.png",
                    ),
                ),
                fec.TourStep(
                    target=self.upload_initiate_button.element_id,
                    description="Click here to start the upload process.",
                    action=fec.TourStepAction(
                        target_id=self.upload_initiate_button.element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="Once it's finished, the uploaded data is now visualized.",
                ),
            ],
            "Overview": [
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="First, we load some data into Lipidome Projector. Learn how to to this in the 'Load data' tour.",
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_modal.load_dataset_button_element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="This is the main graph of Lipidome Projector. Here you can visualize lipidomes among other aspects.",
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="This is the lipidome grid. Here you can see the lipidomes in a table and all the lipids, occuring in them with their abundances.",
                    action=fec.TourStepAction(
                        target_id=self.grid_tabs.element_id,
                        target_prop="value",
                        value="lipidome",
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="You can select some of the lipidomes and make some adjustments or run some operations on them. Learn more about this in the 'Data Operations' and 'Graph Settings' tour. "
                    "Also note, that each column of the grid has a filter.",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_grid.element_id,
                        target_prop="selectedRows",
                        value={"ids": ["1", "2", "3"]},
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="You can also select some lipids on the lipidome graph by using the mode bar's select tools.",
                    image=fec.TourStepImage(
                        src="modebar_select.png",
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="Once selected, the lipids are highlighted in the 'Lipids' tab of the main grid.",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_graph.element_id,
                        target_prop="selectedData",
                        value={
                            "points": [
                                {
                                    "curveNumber": 0,
                                    "pointNumber": 1094,
                                    "pointIndex": 1094,
                                    "x": -26.5841431993342,
                                    "y": -5.370992532852329,
                                    "marker.color": "#EECA3B",
                                    "marker.symbol": 1,
                                    "marker.size": 63,
                                    "marker.line.color": "#cfa600",
                                    "customdata": [
                                        "GUT_YF",
                                        "PA 34:1",
                                        "GP",
                                        0.1913304633950688,
                                    ],
                                },
                                {
                                    "curveNumber": 0,
                                    "pointNumber": 1256,
                                    "pointIndex": 1256,
                                    "x": -26.5841431993342,
                                    "y": -5.370992532852329,
                                    "marker.color": "#54A24B",
                                    "marker.symbol": 1,
                                    "marker.size": 59,
                                    "marker.line.color": "#317d28",
                                    "customdata": [
                                        "GUT_PF",
                                        "PA 34:1",
                                        "GP",
                                        0.1366930849718015,
                                    ],
                                },
                                {
                                    "curveNumber": 0,
                                    "pointNumber": 1538,
                                    "pointIndex": 1538,
                                    "x": -26.5841431993342,
                                    "y": -5.370992532852329,
                                    "marker.color": "#F58518",
                                    "marker.symbol": 1,
                                    "marker.size": 55,
                                    "marker.line.color": "#bc5c00",
                                    "customdata": [
                                        "WING_DISC_YF",
                                        "PA 34:1",
                                        "GP",
                                        0.0719153202695131,
                                    ],
                                },
                            ],
                            "range": {
                                "x": [
                                    -27.613147276204547,
                                    -25.688270862822666,
                                ],
                                "y": [-5.446199474171925, -3.9587949729222895],
                            },
                        },
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.element_id,
                    description="This tab features all of the main functionalities ('Data Setup', 'Graph Settings', 'Data Operations', 'Abundance Chart', 'Representative Structure', 'App Settings' and 'Manual'). Learn more about them in the according tours",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_graph.element_id,
                        target_prop="hoverData",
                        value={
                            "points": [
                                {
                                    "curveNumber": 0,
                                    "pointNumber": 1432,
                                    "pointIndex": 1432,
                                    "x": -26.37259755262582,
                                    "y": 54.3269032765993,
                                    "marker.color": "#4C78A8",
                                    "marker.symbol": 1,
                                    "marker.size": 56,
                                    "marker.line.color": "#285382",
                                    "bbox": {
                                        "x0": 985.35,
                                        "x1": 987.35,
                                        "y0": 313.18,
                                        "y1": 315.18,
                                    },
                                    "customdata": [
                                        "BRAIN_PF",
                                        "PE O- 38:5",
                                        "GP",
                                        0.0903515087929207,
                                    ],
                                }
                            ]
                        },
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.structure_id,
                    description="When you hover over a lipid in the lipidome graph, you can see its representative molecular structure in this tab.",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.structure_id,
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.abundance_chart_id,
                    description="You can also see the abundances of the hovered lipid across the lipidomes.",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.abundance_chart_id,
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.element_id,
                    description="You can adjust the sizes of the three main panels (lipidome graph, settings accordion and the grids) by moving the border between them.",
                    action=fec.TourStepAction(
                        target_id=self.split_horizontal.element_id,
                        target_prop="sizes",
                        value=(70, 30),
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.app_settings_id,
                    description="In this tab, you can change the color mode of the app ...",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.app_settings_id,
                    ),
                ),
                fec.TourStep(
                    target=self.theme_switch.element_id,
                    description="... to be light or dark.",
                    action=fec.TourStepAction(
                        target_id=self.theme_switch.switch_id,
                        target_prop="value",
                        value=True,
                    ),
                ),
            ],
            "Graph Settings": [
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="First, we load some data into Lipidome Projector. Learn how to to this in the 'Load data' tour.",
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_modal.load_dataset_button_element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.graph_settings_id,
                    description="Then navigate to the graph settings section.",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.graph_settings_id,
                    ),
                ),
                fec.TourStep(
                    target=self.dimensionality_selection.element_id,
                    description="Pretty straight forward, you can choose the dimensionality of the graph here.",
                    action=fec.TourStepAction(
                        target_id=self.dimensionality_selection.element_id,
                        target_prop="value",
                        value=3,
                    ),
                ),
                fec.TourStep(
                    target=self.sizemode_selection.element_id,
                    description="In the same manner, you could also choose the size mode of the graph. You can choose whether the lipid abundances should be proportional to the area or the diameter of the markers.",
                ),
                fec.TourStep(
                    target=self.scaling.element_id,
                    description="Here, you can adjust the scaling of the graph. For example, you can choose the scaling function to be linear...",
                    action=fec.TourStepAction(
                        target_id=self.scaling.element_id,
                        target_prop="value",
                        value="linear",
                    ),
                ),
                fec.TourStep(
                    target=self.linear_scaling.factor_element_id,
                    description="... as well as for example the base for the linear scaling.",
                    action=fec.TourStepAction(
                        target_id=self.linear_scaling.factor_element_id,
                        target_prop="value",
                        value=90,
                    ),
                ),
                fec.TourStep(
                    target=self.figure_download_settings.element_id,
                    description="You can also adjust the figure download settings here. For example, you can choose the image file to be a png.",
                    action=fec.TourStepAction(
                        target_id=self.figure_download_settings.file_type_dropdown_id,
                        target_prop="value",
                        value="png",
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="To download a snapshot of the graph, click on the foto icon on in the graph's mode bar to the left.",
                    image=fec.TourStepImage(
                        src="modebar_camera.png",
                    ),
                ),
            ],
            "Data Operations": [
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="First, we load some data into Lipidome Projector. Learn how to to this in the 'Load data' tour.",
                    action=fec.TourStepAction(
                        target_id=self.default_dataset_modal.load_dataset_button_element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.data_operations_id,
                    description="Then navigate to the data operations section.",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.data_operations_id,
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="To create a grouped lipidome, navigate to the lipidome grid ...",
                    action=fec.TourStepAction(
                        target_id=self.grid_tabs.element_id,
                        target_prop="value",
                        value="lipidome",
                    ),
                ),
                fec.TourStep(
                    target=self.grouping_component.dropdown_id,
                    description="... and choose a function for the grouping. We'll leave it as 'mean' for now. This means that we create a new lipidome whose vectors are the mean of the lipidomes, selected in the next step.",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_grid.element_id,
                        target_prop="scrollTo",
                        value={"rowIndex": 1},
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="To do so, select some lipidomes in the grid.",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_grid.element_id,
                        target_prop="selectedRows",
                        value={"ids": ["1", "2", "3"]},
                    ),
                ),
                fec.TourStep(
                    target=self.grouping_component.input_id,
                    description="Choose a name for the grouping.",
                    action=fec.TourStepAction(
                        target_id=self.grouping_component.input_id,
                        target_prop="value",
                        value="Mean of 'BRAIN_YF', 'FAT_BODY_PF' and 'FAT_BODY_YF'",
                    ),
                ),
                fec.TourStep(
                    target=self.grouping_component.button_id,
                    description="Click here to create the grouped lipidome.",
                    action=fec.TourStepAction(
                        target_id=self.grouping_component.button_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="The grouped lipidome is now created, scrolled to...",
                ),
                fec.TourStep(
                    target=self.lipidome_graph.element_id,
                    description="...and visualized.",
                ),
                fec.TourStep(
                    target=self.change_component.dropdown_id,
                    description="To compute pairwise differences between lipidomes, first chose a function for doing so, like 'Difference'. This means that an array with differences of the abundances between the selected lipidomes is computed.",
                    action=fec.TourStepAction(
                        target_id=self.grid_tabs.element_id,
                        target_prop="value",
                        value="lipidome",
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="Next, select at least two lipidomes in the lipidome grid. In this case, we chose 'GUT_PF', 'GUT_YF' and 'LIPOPROTEIN_YF'.",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_grid.element_id,
                        target_prop="selectedRows",
                        value={"ids": ["4", "5", "7"]},
                    ),
                ),
                fec.TourStep(
                    target=self.change_component.button_id,
                    description="Click here to compute the differences.",
                    action=fec.TourStepAction(
                        target_id=self.change_component.button_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.difference_grid.element_id,
                    description="They are now displayed in the difference grid.",
                ),
                fec.TourStep(
                    target=self.settings_accordion.graph_settings_id,
                    description="To see those changes as a graph, navigate to the graph settings.",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.graph_settings_id,
                    ),
                ),
                fec.TourStep(
                    target=self.mode_selection.element_id,
                    description="Then, choose the mode of the graph accordingly...",
                    action=fec.TourStepAction(
                        target_id=self.mode_selection.element_id,
                        target_prop="value",
                        value="difference",
                    ),
                ),
                fec.TourStep(
                    target=self.difference_grid.element_id,
                    description="...as well as a specific difference to visualize.",
                    action=fec.TourStepAction(
                        target_id=self.difference_grid.element_id,
                        target_prop="selectedRows",
                        value={"ids": ["1"]},
                    ),
                ),
                fec.TourStep(
                    target=self.mode_selection.element_id,
                    description="For now, let's switch back to the lipidome overlay mode, ...",
                    action=fec.TourStepAction(
                        target_id=self.mode_selection.element_id,
                        target_prop="value",
                        value="overlay",
                    ),
                ),
                fec.TourStep(
                    target=self.settings_accordion.data_setup_id,
                    description="...to the Data Operations section...",
                    action=fec.TourStepAction(
                        target_id=self.settings_accordion.element_id,
                        target_prop="active_item",
                        value=self.settings_accordion.data_operations_id,
                    ),
                ),
                fec.TourStep(
                    target=self.grid_tabs.element_id,
                    description="... and to the lipidome grid to make some changes there.",
                    action=fec.TourStepAction(
                        target_id=self.grid_tabs.element_id,
                        target_prop="value",
                        value="lipidome",
                    ),
                ),
                fec.TourStep(
                    target=self.set_color_component.set_color_picker_id,
                    description="To set the color of a lipidome, choose a color, ...",
                    action=fec.TourStepAction(
                        target_id=self.set_color_component.set_color_picker_id,
                        target_prop="value",
                        value="#FF0000",
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="...select a lipidome in the lipidome grid...",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_grid.element_id,
                        target_prop="selectedRows",
                        value={"ids": ["7"]},
                    ),
                ),
                fec.TourStep(
                    target=self.set_color_component.set_color_button_id,
                    description="...and click here to set the color.",
                    action=fec.TourStepAction(
                        target_id=self.set_color_component.set_color_button_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.set_name_component.element_id,
                    description="Likewise, to rename the same lipidome, choose a name, like 'My lipidome'...",
                    action=fec.TourStepAction(
                        target_id=self.set_name_component.input_element_id,
                        target_prop="value",
                        value="My lipidome",
                    ),
                ),
                fec.TourStep(
                    target=self.set_name_component.button_element_id,
                    description="... and click here to set it.",
                    action=fec.TourStepAction(
                        target_id=self.set_name_component.button_element_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.set_color_component.color_scale_dropdown_id,
                    description="You can also set a color scale for a set of lipidomes. To do so, choose a color scale, like 'Vivid'.",
                    action=fec.TourStepAction(
                        target_id=self.set_color_component.color_scale_dropdown_id,
                        target_prop="value",
                        value="Vivid",
                    ),
                ),
                fec.TourStep(
                    target=self.lipidome_grid.element_id,
                    description="Select some lipidomes...",
                    action=fec.TourStepAction(
                        target_id=self.lipidome_grid.element_id,
                        target_prop="selectedRows",
                        value={"ids": ["1", "2", "3", "5", "6", "7"]},
                    ),
                ),
                fec.TourStep(
                    target=self.set_color_component.color_scale_button_id,
                    description="...and click here to set the color scale.",
                    action=fec.TourStepAction(
                        target_id=self.set_color_component.color_scale_button_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.delete_component.button_id,
                    description="Finally, to delete some lipidomes, click here.",
                    action=fec.TourStepAction(
                        target_id=self.delete_component.button_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
                fec.TourStep(
                    target=self.delete_component.button_undo_id,
                    description="To undo the deletion, click here.",
                    action=fec.TourStepAction(
                        target_id=self.delete_component.button_undo_id,
                        target_prop="n_clicks",
                        value=1,
                    ),
                ),
            ],
        }
        return tours

    def gen_layout(
        self, dataset_descriptions: dict[str, str], col_names: ColNames
    ) -> html.Div:
        # tour components
        tours: dict[str, list[fec.TourStep]] = self._get_tours()
        tour_components: list[Component] = (
            self.tour_handler.gen_tour_components(tours)
        )
        manual_tour_component: Component = (
            self.manual_tour_component.get_component(tours)
        )

        # components
        fullscreen_size_store: Component = (
            self.fullscreen_size_store.get_component()
        )

        last_deleted_store: Component = self.last_deleted_store.get_component()

        test_warning_modal: Component = self.test_warning.get_component()

        problem_modal: Component = self.problem_modal.get_component()

        upload_setup_button: Component = (
            self.upload_setup_button.get_component()
        )

        default_dataset_button: Component = (
            self.default_dataset_button.get_component()
        )

        mode_selection_div: Component = self.mode_selection.get_component()

        dimensionality_selection_div: Component = (
            self.dimensionality_selection.get_component()
        )

        sizemode_selection_div: Component = (
            self.sizemode_selection.get_component()
        )

        linear_scaling: Component = self.linear_scaling.get_component()

        min_max_scaling: Component = self.min_max_scaling.get_component()

        scaling: Component = self.scaling.get_component(
            linear_scaling=linear_scaling, min_max_scaling=min_max_scaling
        )

        figure_download_settings: Component = (
            self.figure_download_settings.get_component()
        )

        lipidome_graph: Component = self.lipidome_graph.get_component()

        lipidome_graph_fullscreen_button: Component = (
            self.lipidome_graph_fullscreen_button.get_component()
        )

        lipidome_graph_fullscreen_modal: Component = (
            self.lipidome_graph_fullscreen_modal.get_component()
        )

        abundance_graph: Component = self.abundance_graph.get_component()

        abundance_graph_fullscreen_button: Component = (
            self.abundance_graph_fullscreen_button.get_component()
        )

        abundance_graph_fullscreen_modal: Component = (
            self.abundance_graph_fullscreen_modal.get_component()
        )

        structure_image: Component = self.structure_image.get_component()

        structure_image_fullscreen_button: Component = (
            self.structure_image_fullscreen_button.get_component()
        )

        structure_image_fullscreen_modal: Component = (
            self.structure_image_fullscreen_modal.get_component()
        )

        theme_switch: Component = self.theme_switch.get_component()

        about_button: Component = self.about_button.get_component()

        about_modal: Component = self.about_modal.get_component()

        grouping_component: Component = self.grouping_component.get_component()

        change_component = self.change_component.get_component()

        set_color_component: Component = (
            self.set_color_component.get_component()
        )

        set_name_component: Component = self.set_name_component.get_component()

        delete_component: Component = self.delete_component.get_component()

        settings_accordion: Component = self.settings_accordion.get_component(
            upload_setup_button=upload_setup_button,
            default_dataset_button=default_dataset_button,
            mode_selection_div=mode_selection_div,
            dimensionality_selection_div=dimensionality_selection_div,
            sizemode_selection_div=sizemode_selection_div,
            scaling=scaling,
            change_component=change_component,
            grouping_component=grouping_component,
            set_name_component=set_name_component,
            set_color_component=set_color_component,
            delete_component=delete_component,  # noqa: E501
            abundance_graph=abundance_graph,
            abundance_graph_fullscreen_button=abundance_graph_fullscreen_button,  # noqa: E501
            structure_image=structure_image,
            structure_image_fullscreen_button=structure_image_fullscreen_button,  # noqa: E501
            theme_switch=theme_switch,
            about_button=about_button,
            figure_download_settings=figure_download_settings,
            manual_tour_component=manual_tour_component,
        )

        lipidome_grid: Component = self.lipidome_grid.get_component(
            col_names.row_id
        )
        lipid_grid: Component = self.lipid_grid.get_component(col_names.lipid)
        difference_grid: Component = self.difference_grid.get_component()
        log2fc_grid: Component = self.log2fc_grid.get_component()

        grid_tabs: Component = self.grid_tabs.get_component(
            lipidome_grid=lipidome_grid,
            lipid_grid=lipid_grid,
            difference_grid=difference_grid,
            log2fc_grid=log2fc_grid,
        )

        upload_abundances: Component = self.upload_abundances.get_component()

        upload_lipidome_features: Component = (
            self.upload_lipidome_features.get_component()
        )

        upload_fa_constraints: Component = (
            self.upload_fa_constraints.get_component()
        )

        upload_lcb_constraints: Component = (
            self.upload_lcb_constraints.get_component()
        )

        upload_initiate_button: Component = (
            self.upload_initiate_button.get_component()
        )

        upload_failures_grid: Component = (
            self.upload_failures_grid.get_component()
        )

        upload_modal: Component = self.upload_modal.get_component(
            upload_abundances=upload_abundances,
            upload_lipidome_features=upload_lipidome_features,
            upload_fa_constraints=upload_fa_constraints,
            upload_lcb_constraints=upload_lcb_constraints,
            upload_initiate_button=upload_initiate_button,
            upload_failures_grid=upload_failures_grid,
        )

        default_dataset_modal: Component = (
            self.default_dataset_modal.get_component(
                dataset_descriptions=dataset_descriptions
            )
        )

        split_horizontal: Component = self.split_horizontal.gen_component(
            children=[
                html.Div([lipidome_graph_fullscreen_button, lipidome_graph]),
                settings_accordion,
            ],
        )

        split_vertical: Component = self.split_vertical.gen_component(
            children=[
                split_horizontal,
                grid_tabs,
            ],
        )

        main_layout: html.Div = html.Div(
            className="dbc dbc-ag-grid main-div",
            children=[
                split_vertical,
                test_warning_modal,
                problem_modal,
                upload_modal,
                default_dataset_modal,
                abundance_graph_fullscreen_modal,
                lipidome_graph_fullscreen_modal,
                structure_image_fullscreen_modal,
                about_modal,
                fullscreen_size_store,
                last_deleted_store,
                *tour_components,
            ],
        )

        return main_layout
