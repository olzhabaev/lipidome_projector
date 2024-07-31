"""Module concerning the covering random walk radius atom "
"bit sentences descriptor."""

import logging

from collections.abc import Generator
from pathlib import Path

from lipid_vector_space.bit2vec.base_sentences import (
    BaseMolSentences,
    BaseMolSentencesSeriesLoader,
)
from lipid_vector_space.descriptors.atom_radius_bit_map import AtomRadiusBitMap
from lipid_vector_space.descriptors.covering_random_walks import (
    CoveringRandomWalks,
)
from lipid_vector_space.util.iteration_util import SeriesWrapperIter
from lipid_vector_space.util.io_util import (
    chk_files_exist,
    SeriesFromFilesGenerator,
)


logger: logging.Logger = logging.getLogger(__name__)


class RandomWalkSentences(BaseMolSentences):
    def __init__(
        self,
        atom_radius_bit_map: AtomRadiusBitMap,
        random_walks: CoveringRandomWalks,
    ) -> None:
        super().__init__(atom_radius_bit_map)
        self._random_walks: CoveringRandomWalks = random_walks

    def get_structured_sentences(self, radii: list[int]) -> list[list[str]]:
        random_walk_sentences_gen: Generator[list[str], None, None] = (
            [
                str(self._atom_radius_bit_map.atom_radius_bit_dict[atom][r])
                for atom in random_walk
                if r in self._atom_radius_bit_map.atom_radius_bit_dict[atom]
            ]
            for random_walk in self._random_walks.walks
            for r in radii
        )

        random_walk_sentences: list[list[str]] = [
            sentence for sentence in random_walk_sentences_gen if sentence
        ]

        return random_walk_sentences


class RandomWalkSentencesLoader(BaseMolSentencesSeriesLoader):
    def __init__(
        self,
        atom_radius_bit_map_paths: list[Path],
        covering_random_walks_paths: list[Path],
        shuffle: bool,
    ) -> None:
        super().__init__(atom_radius_bit_map_paths, shuffle)
        self._covering_random_walks_paths: list[Path] = (
            covering_random_walks_paths
        )
        chk_files_exist(self._covering_random_walks_paths)

    def _gen_sentences_series_iter(
        self,
        atom_radius_bit_map_series_iter: SeriesWrapperIter,
        shuffle_index: list[int] | None = None,
    ) -> SeriesWrapperIter:
        if shuffle_index is None:
            paths: list[Path] = self._covering_random_walks_paths
        else:
            paths: list[Path] = self._get_shuffled_paths(
                self._covering_random_walks_paths, shuffle_index
            )

        covering_random_walks_series_iter: SeriesWrapperIter = (
            SeriesWrapperIter.from_series_iter(
                SeriesFromFilesGenerator(paths)
            ).derive(CoveringRandomWalks.deserialize)
        )

        sentences_series_iter: SeriesWrapperIter = (
            atom_radius_bit_map_series_iter.combine(
                covering_random_walks_series_iter,
                lambda atom_radius_bit_map, covering_random_walks: (
                    RandomWalkSentences(
                        atom_radius_bit_map, covering_random_walks
                    )
                ),
            )
        )

        return sentences_series_iter
