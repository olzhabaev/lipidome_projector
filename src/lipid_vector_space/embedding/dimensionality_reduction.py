"""Module concerning the dimensionality reduction of embeddings."""

import logging

import pandas as pd

from openTSNE.sklearn import TSNE as OTSNE
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE as SKLTSNE
from umap import UMAP


logger: logging.Logger = logging.getLogger(__name__)


def pca(df: pd.DataFrame, n_components: int) -> pd.DataFrame:
    """Apply Principal Component Analysis (PCA) to a DataFrame.
    :param df: Input DataFrame.
    :param n_components: Number of components.
    :return: Transformed DataFrame.
    """
    return pd.DataFrame(
        PCA(n_components).fit_transform(df.values), index=df.index
    )


def tsne_sklearn(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Apply t-SNE using scikit-learn to a DataFrame.
    :param df: Input DataFrame.
    :param kwargs: Additional keyword arguments.
    :return: Transformed DataFrame.
    """
    return pd.DataFrame(
        SKLTSNE(**kwargs).fit_transform(df.values), index=df.index
    )


def tsne_opentsne(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Apply t-SNE using openTSNE to a DataFrame.
    :param df: Input DataFrame.
    :param kwargs: Additional keyword arguments.
    :return: Transformed DataFrame.
    """
    return pd.DataFrame(
        OTSNE(**kwargs).fit_transform(df.values), index=df.index
    )


def umap(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Apply UMAP to a DataFrame.
    :param df: Input DataFrame.
    :param kwargs: Additional keyword arguments.
    :return: Transformed DataFrame.
    """
    return pd.DataFrame(
        UMAP(**kwargs).fit_transform(df.values), index=df.index
    )
