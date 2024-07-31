"""Module concerning the scaling of embeddings."""

import logging

import pandas as pd

from sklearn.preprocessing import MinMaxScaler


logger: logging.Logger = logging.getLogger(__name__)


def linear_scaling[
    PDObjType: (pd.DataFrame, pd.Series)
](df: PDObjType, factor: float, base: float) -> PDObjType:
    """Apply linear scaling to a DataFrame.
    :param df: Input DataFrame.
    :param factor: Scaling factor.
    :param base: Offset.
    :return: Scaled DataFrame.
    """
    return df * factor + base


def min_max_series(series: pd.Series, min_val: int, max_val: int) -> pd.Series:
    """Apply min-max scaling to a Series.
    :param series: Input Series.
    :param min_val: Minimum value.
    :param max_val: Maximum value.
    :return: Scaled Series.
    """
    return pd.Series(
        MinMaxScaler(feature_range=(min_val, max_val))
        .fit_transform(series.to_numpy().reshape(-1, 1))
        .reshape(series.shape),
        index=series.index,
        name=series.name,
    )


def min_max_df_full(
    df: pd.DataFrame, min_val: int, max_val: int
) -> pd.DataFrame:
    """Apply min-max scaling to a DataFrame.
    :param df: Input DataFrame.
    :param min_val: Minimum value.
    :param max_val: Maximum value.
    :return: Scaled DataFrame.
    """
    return pd.DataFrame(
        MinMaxScaler(feature_range=(min_val, max_val))
        .fit_transform(df.to_numpy().reshape(-1, 1))
        .reshape(df.shape),
        columns=df.columns,
        index=df.index,
    )


def min_max_df_column_wise(
    df: pd.DataFrame, min_val: int, max_val: int
) -> pd.DataFrame:
    """Apply min-max scaling column-wise to a DataFrame.
    :param df: Input DataFrame.
    :param min_val: Minimum value.
    :param max_val: Maximum value.
    :return: Scaled DataFrame.
    """
    return pd.DataFrame(
        MinMaxScaler(feature_range=(min_val, max_val)).fit_transform(
            df.to_numpy()
        ),
        columns=df.columns,
        index=df.index,
    )
