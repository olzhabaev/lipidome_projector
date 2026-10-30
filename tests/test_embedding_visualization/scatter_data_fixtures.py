"""Module concerning scatter data fixtures."""

import logging

import pandas as pd
import pytest

from embedding_visualization.scatter_data import ScatterData


logger: logging.Logger = logging.getLogger(__name__)


# COLUMNS ---------------------------------------------------------------------


@pytest.fixture(scope="session")
def col_name_x() -> str:
    return "x"


@pytest.fixture(scope="session")
def col_x(col_name_x: str) -> pd.Series:
    return pd.Series([0, 1, 2, 3, 4], name=col_name_x)


@pytest.fixture(scope="session")
def col_name_y() -> str:
    return "y"


@pytest.fixture(scope="session")
def col_y(col_name_y: str) -> pd.Series:
    return pd.Series([1, 2, 3, 4, 5], name=col_name_y)


@pytest.fixture(scope="session")
def col_name_z() -> str:
    return "z"


@pytest.fixture(scope="session")
def col_z(col_name_z: str) -> pd.Series:
    return pd.Series([0, 1, 2, 3, 4], name=col_name_z)


@pytest.fixture(scope="session")
def col_name_cat_1() -> str:
    return "cat_feature_1"


@pytest.fixture(scope="session")
def col_cat_1(col_name_cat_1: str) -> pd.Series:
    return pd.Series(
        ["f1_a", "f1_a", "f1_a", "f1_b", "f1_b"],
        name=col_name_cat_1,
    )


@pytest.fixture(scope="session")
def col_name_cat_2() -> str:
    return "cat_feature_2"


@pytest.fixture(scope="session")
def col_cat_2(col_name_cat_2: str) -> pd.Series:
    return pd.Series(
        ["f2_a", "f2_b", "f2_c", "f2_d", "f2_e"],
        name=col_name_cat_2,
    )


@pytest.fixture(scope="session")
def col_name_cat_3() -> str:
    return "cat_feature_3"


@pytest.fixture(scope="session")
def col_cat_3(col_name_cat_3: str) -> pd.Series:
    return pd.Series(
        ["f3_a", "f3_a", "f3_b", "f3_b", "f3_b"],
        name=col_name_cat_3,
    )


@pytest.fixture(scope="session")
def col_name_num_1() -> str:
    return "num_feature_1"


@pytest.fixture(scope="session")
def col_num_1(col_name_num_1: str) -> pd.Series:
    return pd.Series([0, 1, 2, 3, 4], name=col_name_num_1, dtype=int)


@pytest.fixture(scope="session")
def col_name_num_2() -> str:
    return "num_feature_2"


@pytest.fixture(scope="session")
def col_num_2(col_name_num_2: str) -> pd.Series:
    return pd.Series([0.5, 1.5, 2.5, 3.5, 4.5], name=col_name_num_2)


# DATAFRAMES ------------------------------------------------------------------


@pytest.fixture(scope="session")
def scatter_data_df_2d(
    col_x: pd.Series,
    col_y: pd.Series,
    col_cat_1: pd.Series,
    col_cat_2: pd.Series,
    col_cat_3: pd.Series,
    col_num_1: pd.Series,
    col_num_2: pd.Series,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            col_x.name: col_x,
            col_y.name: col_y,
            col_cat_1.name: col_cat_1,
            col_cat_2.name: col_cat_2,
            col_cat_3.name: col_cat_3,
            col_num_1.name: col_num_1,
            col_num_2.name: col_num_2,
        }
    )


@pytest.fixture(scope="session")
def scatter_data_df_3d(
    col_x: pd.Series,
    col_y: pd.Series,
    col_z: pd.Series,
    col_cat_1: pd.Series,
    col_cat_2: pd.Series,
    col_cat_3: pd.Series,
    col_num_1: pd.Series,
    col_num_2: pd.Series,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            col_x.name: col_x,
            col_y.name: col_y,
            col_z.name: col_z,
            col_cat_1.name: col_cat_1,
            col_cat_2.name: col_cat_2,
            col_cat_3.name: col_cat_3,
            col_num_1.name: col_num_1,
            col_num_2.name: col_num_2,
        }
    )


# # SCATTER DATA --------------------------------------------------------------


@pytest.fixture(scope="session")
def scatter_data_1(
    scatter_data_df_2d: pd.DataFrame,
    col_name_x: str,
    col_name_y: str,
    col_name_cat_1: str,
    col_name_cat_2: str,
    col_name_cat_3: str,
    col_name_num_1: str,
    col_name_num_2: str,
) -> ScatterData:
    scatter_data: ScatterData = ScatterData(
        dataframe=scatter_data_df_2d,
        vector_col_names=[col_name_x, col_name_y],
        color_col_name=col_name_cat_1,
        symbol_col_name=col_name_cat_3,
        size_col_name=col_name_num_1,
        hover_data_col_names=[col_name_num_2],
        annotation_col_names=[col_name_cat_2],
    )

    return scatter_data


# FILTERING -------------------------------------------------------------------


@pytest.fixture(scope="session")
def filtered_name() -> str:
    return "filtered"


@pytest.fixture(scope="session")
def col_cat_2_filter() -> list[str]:
    return ["f2_a", "f2_b", "f2_c"]


@pytest.fixture(scope="session")
def col_cat_2_filtered(filtered_name: str, col_name_cat_2: str) -> pd.Series:
    return pd.Series(
        ["f2_a", "f2_b", "f2_c", filtered_name, filtered_name],
        name=col_name_cat_2,
    )
