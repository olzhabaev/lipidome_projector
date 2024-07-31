"""Module concerning the embedding data structure."""

import logging

from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol, Self

import pandas as pd

from lipid_vector_space.util.io_util import (
    chk_file_exists,
    chk_file_doesnt_exist,
)


logger: logging.Logger = logging.getLogger(__name__)


class TransformerProtocol(Protocol):
    def __call__(
        self, df: pd.DataFrame, **kwargs: dict[str, Any]
    ) -> pd.DataFrame: ...


class Embedding:
    def __init__(self, vectors_df: pd.DataFrame) -> None:
        """Initialize embedding.
        :param vectors: DataFrame of embedding vectors.
        :param model_objects: Dictionary of embedding model objects.
        """
        self._vectors_df: pd.DataFrame = vectors_df

    @classmethod
    @abstractmethod
    def with_training(
        cls, data: Iterable[list], model_params: dict[str, Any], **kwargs: Any
    ) -> Self:
        raise NotImplementedError

    @classmethod
    def from_files(
        cls,
        vec_csv_path: Path,
        index_col: str | int,
    ) -> Self:
        """Create an embedding from a CSV file.
        :param vec_path: Path to the input CSV file.
        :param index_col: Index column name.
        :return: Embedding object.
        """
        chk_file_exists(vec_csv_path)
        logger.info(f"Read vectors from {vec_csv_path}.")
        return cls(pd.read_csv(vec_csv_path, index_col=index_col))

    @property
    def vectors_df(self) -> pd.DataFrame:
        return self._vectors_df

    def save(self, vec_path: Path, **kwargs: Any) -> None:
        """Write embedding to a CSV file.
        :param vec_path: Path to the vectors output CSV file.
        """
        chk_file_doesnt_exist(vec_path)
        logger.info(f"Write embedding vectors to '{vec_path}'.")
        self._vectors_df.to_csv(vec_path)

    def derive(self, transformer: TransformerProtocol, **kwargs: Any) -> Self:
        return type(self)(transformer(self._vectors_df, **kwargs))
