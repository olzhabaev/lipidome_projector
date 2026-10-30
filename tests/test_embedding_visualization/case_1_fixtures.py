"""Test case 1."""

import logging

import pandas as pd
import pytest

from embedding_visualization.marker_maps import MarkerMaps
from embedding_visualization.parameters import PlotlyScatterParameters
from embedding_visualization.scatter_data import ScatterData

from tests.test_embedding_visualization.util import Case


logger: logging.Logger = logging.getLogger(__name__)


# PARAMETERS ------------------------------------------------------------------


@pytest.fixture(scope="session")
def parameters_1() -> PlotlyScatterParameters:
    return PlotlyScatterParameters(explicit_marker_stacking=True)


# MARKER MAPS -----------------------------------------------------------------


@pytest.fixture(scope="session")
def marker_maps_1(
    scatter_data_1: ScatterData, parameters_1: PlotlyScatterParameters
) -> MarkerMaps:
    return MarkerMaps.from_parameters(
        marker_colotype=parameters_1.marker_colortype,
        marker_colormap=parameters_1.marker_colormap,
        marker_symbol_map=None,
        colorscale_name=parameters_1.continuous_colorscale_name,
        color_column=scatter_data_1.color_column,
        symbol_column=scatter_data_1.symbol_column,
        filtered_name=None,
        dimensionality=scatter_data_1.dimensionality,
    )


# TEST CASES ------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_case_1(
    parameters_1: PlotlyScatterParameters,
    marker_maps_1: MarkerMaps,
) -> Case:
    sd_df: pd.DataFrame = pd.DataFrame(
        {
            "x": [0, 1, 2, 3, 4],
            "y": [1, 2, 3, 4, 5],
            "cat_feature_1": ["f1_a", "f1_a", "f1_a", "f1_b", "f1_b"],
            "cat_feature_2": ["f2_a", "f2_b", "f2_c", "f2_d", "f2_e"],
            "cat_feature_3": ["f3_a", "f3_a", "f3_b", "f3_b", "f3_b"],
            "num_feature_1": [0, 1, 2, 3, 4],
            "num_feature_2": [0.5, 1.5, 2.5, 3.5, 4.5],
        }
    )

    scatter_data: ScatterData = ScatterData(
        dataframe=sd_df,
        vector_col_names=["x", "y"],
        color_col_name="cat_feature_1",
        symbol_col_name="cat_feature_3",
        size_col_name="num_feature_1",
        hover_data_col_names=["num_feature_2"],
        annotation_col_names=["cat_feature_2"],
    )

    test_case: Case = Case(
        name="test_case_1",
        scatter_data=scatter_data,
        parameters=parameters_1,
        marker_maps=marker_maps_1,
        x_ref=[4, 3, 2, 1, 0],
        y_ref=[5, 4, 3, 2, 1],
        z_ref=[],
        colors_ref=["#F58518", "#F58518", "#4C78A8", "#4C78A8", "#4C78A8"],
        symbols_ref=[100, 100, 100, 0, 0],
        hoverdata_ref=[
            [4.5],
            [3.5],
            [2.5],
            [1.5],
            [0.5],
        ],
        legend_names_ref=[
            "f1_a, f3_a",
            "f1_a, f3_b",
            "f1_b, f3_a",
            "f1_b, f3_b",
        ],
    )

    return test_case
