"""Module concerning input data processing."""

import logging

from abc import abstractmethod
from collections.abc import Generator, Hashable, Iterable, Iterator
from typing import Any, cast

from gensim.models.doc2vec import TaggedDocument

from lipid_vector_space.bit2vec.base_sentences import (
    BaseMolSentences,
    BaseMolSentencesSeriesLoader,
)
from lipid_vector_space.util.iteration_util import SeriesWrapperIter


logger: logging.Logger = logging.getLogger(__name__)


class BaseInput(Iterable):
    def __init__(
        self,
        sentences_series_loader: BaseMolSentencesSeriesLoader,
        radii: list[int],
    ) -> None:
        self._sentences_series_loader: BaseMolSentencesSeriesLoader = (
            sentences_series_loader
        )
        self._radii: list[int] = radii

    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...


class W2VTrainingInput(BaseInput):
    def __iter__(self) -> Generator[list[str], None, None]:
        sentences_series_iter: SeriesWrapperIter = (
            self._sentences_series_loader.get_sentences_series_iter()
        )

        structured_sentences_iter: SeriesWrapperIter = (
            sentences_series_iter.derive(
                lambda sentences: cast(
                    BaseMolSentences, sentences
                ).get_structured_sentences(self._radii)
            )
        )

        descriptor_iter: Generator[list[str], None, None] = (
            sentence
            for sentences in structured_sentences_iter.get_element_iter()
            for sentence in sentences
        )

        return descriptor_iter


class W2VCompositionInput(BaseInput):
    def __iter__(self) -> Iterable[tuple[Hashable, list[str]]]:
        sentences_series_iter: SeriesWrapperIter = (
            self._sentences_series_loader.get_sentences_series_iter()
        )

        structured_sentences_iter: SeriesWrapperIter = (
            sentences_series_iter.derive(
                lambda sentences: cast(
                    BaseMolSentences, sentences
                ).get_flattened_atom_radius_sentences(self._radii)
            )
        )

        descriptor_iter: Iterable[tuple[Hashable, list[str]]] = (
            structured_sentences_iter.get_indexed_element_iter()
        )

        return descriptor_iter


class D2VTrainingInput(BaseInput):
    def __iter__(self) -> Generator[TaggedDocument, None, None]:
        sentences_series_iter: SeriesWrapperIter = (
            self._sentences_series_loader.get_sentences_series_iter()
        )

        structured_sentences_iter: SeriesWrapperIter = (
            sentences_series_iter.derive(
                lambda sentences: cast(
                    BaseMolSentences, sentences
                ).get_structured_sentences(self._radii)
            )
        )

        descriptor_iter: Generator[TaggedDocument, None, None] = (
            TaggedDocument(words=sentence, tags=[index])
            for index, sentences in structured_sentences_iter.get_indexed_element_iter()  # noqa: E501
            for sentence in sentences
        )

        return descriptor_iter


class InputChain(BaseInput):
    def __init__(self, inputs: list[BaseInput]) -> None:
        self._inputs: list[BaseInput] = inputs

    def __iter__(self) -> Generator[Any, None, None]:
        return (element for input_ in self._inputs for element in input_)
