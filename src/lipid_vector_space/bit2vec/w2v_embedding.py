"""Module concerning the word2vec embedding model."""

import logging

from pathlib import Path
from typing import Any, Iterable, Self

import pandas as pd

from gensim.models import Word2Vec

from lipid_vector_space.embedding.embedding import Embedding
from lipid_vector_space.util.io_util import chk_files_dont_exist


logger: logging.Logger = logging.getLogger(__name__)


class Word2VecEmbedding(Embedding):
    def __init__(
        self,
        vectors_df: pd.DataFrame,
        word_model: Word2Vec,
        word_vectors_df: pd.DataFrame,
    ) -> None:
        super().__init__(vectors_df)
        self._word_model: Word2Vec = word_model
        self._word_vectors_df: pd.DataFrame = word_vectors_df

    @classmethod
    def with_training(
        cls,
        training_data: Iterable[list],
        model_params: dict[str, Any],
        composition_data: Iterable[tuple[str, list]],
    ) -> Self:
        """Train a Word2Vec model.
        :param training_data: The data to train on.
        :param model_params: Word2Vec parameters.
        :param composition_data: Composition data.
        :return: Word2Vec embedding instance.
        """
        logger.info("Train W2V model.")

        word_model: Word2Vec = Word2Vec(training_data, **model_params)

        word_vectors_df: pd.DataFrame = pd.DataFrame(
            word_model.wv.vectors, index=word_model.wv.index_to_key
        )

        sentence_vectors_df: pd.DataFrame = cls._compose_word_vectors(
            word_vectors_df, composition_data
        )

        return cls(sentence_vectors_df, word_model, word_vectors_df)

    def save(
        self, vec_path: Path, sub_vec_path: Path, model_path: Path
    ) -> None:
        """Write embedding to a CSV file.
        :param vec_path: Path to the vectors output CSV file.
        :param sub_vec_path: Path to the substructure vectors output CSV file.
        :param model_path: Path to the model output file.
        """
        chk_files_dont_exist([vec_path, sub_vec_path, model_path])
        super().save(vec_path)
        logger.info(f"Write substructure vectors to '{sub_vec_path}'.")
        self._word_vectors_df.to_csv(sub_vec_path)
        logger.info(f"Write model to '{model_path}'.")
        self._word_model.save(str(model_path))

    @staticmethod
    def _compose_word_vectors(
        vectors_df: pd.DataFrame,
        composition_data: Iterable[tuple[str, list]],
        method: str = "sum",
    ) -> pd.DataFrame:
        vector_composition: pd.DataFrame = pd.DataFrame.from_dict(
            {
                composition_index: vectors_df.loc[vector_indexes].agg(method)
                for composition_index, vector_indexes in composition_data
            },
            orient="index",
        )

        return vector_composition
