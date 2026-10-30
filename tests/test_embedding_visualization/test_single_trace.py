"""Contains tests of the single trace embedding visualization."""

import logging

from pathlib import Path
from typing import cast

import pytest

from _pytest.fixtures import FixtureRequest

from tests.test_embedding_visualization.util import Case

logger: logging.Logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "test_case_name",
    ["test_case_1"],
)
def test_single_trace_scatter_coordinates(
    test_case_name: str, request: FixtureRequest
) -> None:
    test_case: Case = request.getfixturevalue(test_case_name)

    assert all(test_case.x_ref == cast(dict, test_case.figure)["data"][0]["x"])
    assert all(test_case.y_ref == cast(dict, test_case.figure)["data"][0]["y"])

    if test_case.scatter_data.dimensionality == 3:
        assert all(
            test_case.z_ref == cast(dict, test_case.figure)["data"][0]["z"]
        )
    else:
        assert "z" not in cast(dict, test_case.figure)["data"][0]


@pytest.mark.parametrize(
    "test_case_name",
    ["test_case_1"],
)
def test_single_trace_scatter_legend(
    test_case_name: str, request: FixtureRequest
) -> None:
    test_case: Case = request.getfixturevalue(test_case_name)

    assert "" == test_case.figure_dict["data"][0]["name"]
    assert not test_case.figure_dict["data"][0]["showlegend"]
    assert test_case.legend_names_ref == [
        trace["name"]
        for trace in test_case.figure_dict["data"][
            1 : test_case.num_legend_groups + 1  # noqa E203
        ]
    ]
    assert test_case.legend_names_ref == [
        trace["legendgroup"]
        for trace in test_case.figure_dict["data"][
            1 : test_case.num_legend_groups + 1  # noqa E203
        ]
    ]
    assert all(
        trace["showlegend"]
        for trace in test_case.figure_dict["data"][
            1 : test_case.num_legend_groups + 1  # noqa E203
        ]
    )
    assert all(
        (trace["x"] == [None] and trace["y"] == [None])
        for trace in test_case.figure_dict["data"][
            1 : test_case.num_legend_groups + 1  # noqa E203
        ]
    )


@pytest.mark.parametrize(
    "test_case_name",
    ["test_case_1"],
)
def test_hoverdata(test_case_name: str, request: FixtureRequest) -> None:
    test_case: Case = request.getfixturevalue(test_case_name)
    assert (
        test_case.hoverdata_ref
        == (cast(dict, test_case.figure)["data"][0]["customdata"]).tolist()
    )


@pytest.mark.parametrize(
    "test_case_name",
    ["test_case_1"],
)
def test_colors(test_case_name: str, request: FixtureRequest) -> None:
    test_case: Case = request.getfixturevalue(test_case_name)
    assert (
        test_case.colors_ref
        == (test_case.figure_dict["data"][0]["marker"]["color"]).tolist()
    )


@pytest.mark.parametrize(
    "test_case_name",
    ["test_case_1"],
)
def test_symbols(test_case_name: str, request: FixtureRequest) -> None:
    test_case: Case = request.getfixturevalue(test_case_name)
    if test_case.scatter_data.symbol_col_name is None:
        assert "symbol" not in test_case.figure_dict["data"][0]["marker"]
    else:
        assert (
            test_case.symbols_ref
            == (
                cast(dict, test_case.figure)["data"][0]["marker"]["symbol"]
            ).tolist()
        )


@pytest.mark.parametrize(
    "test_case_name",
    ["test_case_1"],
)
def test_write_to_html(
    test_case_name: str, base_dir: Path, request: FixtureRequest
) -> None:
    test_case: Case = request.getfixturevalue(test_case_name)

    test_case.figure.write_html(base_dir / f"{test_case.name}.html")
    assert (base_dir / f"{test_case.name}.html").exists()
