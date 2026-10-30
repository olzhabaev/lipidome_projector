"""Module concerning the testing of scatter data."""

import logging

from typing import cast

import pandas as pd
import pytest

from embedding_visualization.scatter_data import ScatterData


logger: logging.Logger = logging.getLogger(__name__)


def test_scatter_data_creation_success(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_1: str,
    col_name_cat_2: str,
    col_name_cat_3: str,
    col_name_num_1: str,
    col_name_num_2: str,
) -> None:
    scatter_data: ScatterData = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        color_col_name=col_name_cat_1,
        symbol_col_name=col_name_cat_2,
        size_col_name=col_name_num_1,
        hover_data_col_names=[col_name_num_2],
        annotation_col_names=[col_name_cat_3],
    )

    pd.testing.assert_frame_equal(
        scatter_data.dataframe,
        scatter_data_df_2d,
    )


def test_scatter_data_creation_failure_color_column(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
) -> None:
    with pytest.raises(ValueError, match="Color column"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=[col_name_x, col_name_y],
            color_col_name="non_existent_column",
        )


def test_scatter_data_creation_failure_symbol_column(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
) -> None:
    with pytest.raises(ValueError, match="Symbol column"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=[col_name_x, col_name_y],
            symbol_col_name="non_existent_column",
        )


def test_scatter_data_creation_failure_size_column(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
) -> None:
    with pytest.raises(ValueError, match="Size column"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=[col_name_x, col_name_y],
            size_col_name="non_existent_column",
        )


def test_scatter_data_creation_failure_annotation_columns(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
) -> None:
    with pytest.raises(ValueError, match="annotation column"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=[col_name_x, col_name_y],
            annotation_col_names=["non_existent_column"],
        )


def test_scatter_data_creation_failure_hover_data_columns(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
) -> None:
    with pytest.raises(ValueError, match="hoverdata column"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=[col_name_x, col_name_y],
            hover_data_col_names=["non_existent_column"],
        )


def test_scatter_data_creation_failure_vector_columns(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_1: str,
    col_name_cat_2: str,
) -> None:
    with pytest.raises(ValueError, match="vector column"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=["non_existent_column"],
        )

    with pytest.raises(ValueError, match="dimensionality"):
        ScatterData(
            dataframe=scatter_data_df_2d,
            vector_col_names=[
                col_name_x,
                col_name_y,
                col_name_cat_1,
                col_name_cat_2,
            ],
        )


def test_scatter_data_dimensionality_2d(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
) -> None:
    scatter_data: ScatterData = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
    )

    assert scatter_data.dimensionality == 2


def test_scatter_data_dimensionality(
    scatter_data_df_3d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_z: str,
) -> None:
    scatter_data = ScatterData(
        dataframe=scatter_data_df_3d,
        vector_col_names=[col_name_x, col_name_y, col_name_z],
    )

    assert scatter_data.dimensionality == 3


def test_scatter_data_color_column(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_1: str,
) -> None:
    scatter_data = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        color_col_name=col_name_cat_1,
    )

    pd.testing.assert_series_equal(
        cast(pd.Series, scatter_data.color_column),
        scatter_data_df_2d[col_name_cat_1],
    )


def test_scatter_data_symbol_column(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_2: str,
) -> None:
    scatter_data = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        symbol_col_name=col_name_cat_2,
    )

    pd.testing.assert_series_equal(
        cast(pd.Series, scatter_data.symbol_column),
        scatter_data_df_2d[col_name_cat_2],
    )


def test_scatter_data_size_column(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_num_1: str,
) -> None:
    scatter_data: ScatterData = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        size_col_name=col_name_num_1,
    )

    pd.testing.assert_series_equal(
        cast(pd.Series, scatter_data.size_column),
        scatter_data_df_2d[col_name_num_1],
    )


def test_scatter_data_color_filter(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_2: str,
    col_cat_2_filter: list[str],
    col_cat_2_filtered: pd.Series,
    filtered_name: str,
) -> None:
    scatter_data: ScatterData = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        color_col_name=col_name_cat_2,
        color_filter=col_cat_2_filter,
        filtered_name=filtered_name,
    )

    pd.testing.assert_series_equal(
        col_cat_2_filtered,
        cast(pd.Series, scatter_data.color_column),
    )


def test_scatter_data_symbol_filter(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_2: str,
    col_cat_2_filter: list[str],
    col_cat_2_filtered: pd.Series,
    filtered_name: str,
) -> None:
    scatter_data: ScatterData = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        symbol_col_name=col_name_cat_2,
        symbol_filter=col_cat_2_filter,
        filtered_name=filtered_name,
    )

    pd.testing.assert_series_equal(
        col_cat_2_filtered,
        cast(pd.Series, scatter_data.symbol_column),
    )
