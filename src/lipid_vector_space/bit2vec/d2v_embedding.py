"""Module concerning the doc2vec embedding model."""

import logging

from pathlib import Path
from typing import Any, Iterable, Self

import pandas as pd

from gensim.models import Doc2Vec

from lipid_vector_space.embedding.embedding import Embedding
from lipid_vector_space.util.io_util import chk_files_dont_exist


logger: logging.Logger = logging.getLogger(__name__)


class Doc2VecEmbedding(Embedding):
    def __init__(
        self,
        vectors_df: pd.DataFrame,
        model: Doc2Vec,
    ) -> None:
        super().__init__(vectors_df)
        self._model: Doc2Vec = model

    @classmethod
    def with_training(
        cls, training_data: Iterable[list], model_params: dict[str, Any]
    ) -> Self:
        """Train a Doc2Vec model.
        :param training_data: The data to train on.
        :param model_params: Doc2Vec parameters.
        :return: Doc2Vec embedding instance.
        """
        logger.info("Train D2V model.")

        model: Doc2Vec = Doc2Vec(training_data, **model_params)

        vectors_df: pd.DataFrame = pd.DataFrame(
            model.dv.vectors, index=model.dv.index_to_key
        )

        return cls(vectors_df, model)

    def save(self, vec_path: Path, model_path: Path) -> None:
        """Write embedding to a CSV file.
        :param vec_path: Path to the vectors output CSV file.
        :param model_path: Path to the model output file.
        """
        chk_files_dont_exist([vec_path, model_path])
        super().save(vec_path)
        logger.info(f"Write model to '{model_path}'.")
        self._model.save(str(model_path))
