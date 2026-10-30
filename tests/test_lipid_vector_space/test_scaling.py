"""Module concerning the testing of scaling."""

import logging

import pandas as pd

from lipid_vector_space.embedding.scaling import linear_scaling, min_max_series


logger: logging.Logger = logging.getLogger(__name__)


def test_min_max_series_single_value():
    series = pd.Series([5])
    scaled = min_max_series(series, 0, 1)
    assert scaled.iloc[0] == 0


def test_min_max_series_uniform():
    series = pd.Series([5, 5, 5])
    scaled = min_max_series(series, 0, 1)
    assert all(scaled == 0)


def test_min_max_series_normal():
    series = pd.Series([1, 2, 3, 4, 5])
    scaled = min_max_series(series, 1, 12)
    pd.testing.assert_series_equal(scaled, pd.Series([1, 3.75, 6.5, 9.25, 12]))


def test_min_max_series_out_of_order():
    series = pd.Series([5, 2, 4, 0, 3, 1])
    scaled = min_max_series(series, 20, 70)
    pd.testing.assert_series_equal(
        scaled, pd.Series([70, 40, 60, 20, 50, 30]), check_dtype=False
    )


def test_min_max_series_negative_values():
    series = pd.Series([-5, -3, -1])
    scaled = min_max_series(series, 0, 1)
    assert scaled.min() == 0 and scaled.max() == 1


def test_linear_scaling_single_column():
    df = pd.DataFrame({"A": [1, 2, 3]})
    scaled = linear_scaling(df, 2, 1)
    expected = pd.DataFrame({"A": [3, 5, 7]})
    pd.testing.assert_frame_equal(scaled, expected)


def test_linear_scaling_multi_column():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    scaled = linear_scaling(df, 2, -1)
    expected = pd.DataFrame({"A": [1, 3, 5], "B": [7, 9, 11]})
    pd.testing.assert_frame_equal(scaled, expected)


def test_linear_scaling_series():
    series = pd.Series([1, 2, 3])
    scaled = linear_scaling(series, 3, 0)
    expected = pd.Series([3, 6, 9])
    pd.testing.assert_series_equal(scaled, expected)


def test_linear_scaling_negative_values():
    df = pd.DataFrame({"A": [-3, -2, -1]})
    scaled = linear_scaling(df, 2, 5)
    expected = pd.DataFrame({"A": [-1, 1, 3]})
    pd.testing.assert_frame_equal(scaled, expected)


def test_linear_scaling_zero_factor():
    df = pd.DataFrame({"A": [1, 2, 3]})
    scaled = linear_scaling(df, 0, 10)
    expected = pd.DataFrame({"A": [10, 10, 10]})
    pd.testing.assert_frame_equal(scaled, expected)


def test_linear_scaling_zero_base():
    df = pd.DataFrame({"A": [1, 2, 3]})
    scaled = linear_scaling(df, 2, 0)
    expected = pd.DataFrame({"A": [2, 4, 6]})
    pd.testing.assert_frame_equal(scaled, expected)
