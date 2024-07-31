"""Module concerning mol sentences descriptor base classes."""

import logging

from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path
from random import sample

from lipid_vector_space.descriptors.atom_radius_bit_map import AtomRadiusBitMap
from lipid_vector_space.util.iteration_util import SeriesWrapperIter
from lipid_vector_space.util.io_util import (
    chk_files_exist,
    SeriesFromFilesGenerator,
)


logger: logging.Logger = logging.getLogger(__name__)


class BaseMolSentences(ABC):
    def __init__(self, atom_radius_bit_map: AtomRadiusBitMap) -> None:
        self._atom_radius_bit_map: AtomRadiusBitMap = atom_radius_bit_map

    @abstractmethod
    def get_structured_sentences(self, radii: list[int]) -> list[list]: ...

    def get_radius_atom_sentences(self, radii: list[int]) -> list[list[str]]:
        radius_atom_sentences_gen: Generator[list[str], None, None] = (
            [
                str(self._atom_radius_bit_map.atom_radius_bit_dict[atom][r])
                for atom in self._atom_radius_bit_map.atoms
                if r in self._atom_radius_bit_map.atom_radius_bit_dict[atom]
            ]
            for r in radii
        )

        radius_atom_sentences: list[list[str]] = [
            sentence for sentence in radius_atom_sentences_gen if sentence
        ]

        return radius_atom_sentences

    def get_flattened_atom_radius_sentences(
        self, radii: list[int]
    ) -> list[str]:
        return [
            word
            for sentence in self.get_radius_atom_sentences(radii)
            for word in sentence
        ]


class BaseMolSentencesSeriesLoader(ABC):
    def __init__(
        self, atom_radius_bit_map_paths: list[Path], shuffle: bool
    ) -> None:
        self._atom_radius_bit_map_paths: list[Path] = atom_radius_bit_map_paths
        self._shuffle: bool = shuffle
        chk_files_exist(self._atom_radius_bit_map_paths)

    def get_sentences_series_iter(self) -> SeriesWrapperIter:
        shuffle_index: list[int] | None = (
            self._gen_shuffle_index(len(self._atom_radius_bit_map_paths))
            if self._shuffle
            else None
        )

        atom_radius_bit_map_series_iter: SeriesWrapperIter = (
            self._load_atom_radius_bit_map_series_iter(shuffle_index)
        )

        sentences_series_iter: SeriesWrapperIter = (
            self._gen_sentences_series_iter(
                atom_radius_bit_map_series_iter, shuffle_index
            )
        )

        if self._shuffle:
            sentences_series_iter = sentences_series_iter.shuffle_each()

        return sentences_series_iter

    @abstractmethod
    def _gen_sentences_series_iter(
        self,
        atom_radius_bit_map_series_iter: SeriesWrapperIter,
        shuffle_index: list[int] | None = None,
    ) -> SeriesWrapperIter: ...

    def _load_atom_radius_bit_map_series_iter(
        self, shuffle_index: list[int] | None = None
    ) -> SeriesWrapperIter:
        if shuffle_index is None:
            paths: list[Path] = self._atom_radius_bit_map_paths
        else:
            paths: list[Path] = self._get_shuffled_paths(
                self._atom_radius_bit_map_paths, shuffle_index
            )

        return SeriesWrapperIter.from_series_iter(
            SeriesFromFilesGenerator(paths)
        ).derive(AtomRadiusBitMap.deserialize)

    @staticmethod
    def _get_shuffled_paths(
        paths: list[Path], shuffle_index: list[int]
    ) -> list[Path]:
        return [paths[i] for i in shuffle_index]

    @staticmethod
    def _gen_shuffle_index(length: int) -> list[int]:
        return sample(range(length), length)
