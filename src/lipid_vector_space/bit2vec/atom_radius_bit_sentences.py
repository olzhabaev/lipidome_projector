"""Module concerning the atom-radius-bit sentences descriptor."""

import logging

from lipid_vector_space.util.iteration_util import SeriesWrapperIter
from lipid_vector_space.bit2vec.base_sentences import (
    BaseMolSentences,
    BaseMolSentencesSeriesLoader,
)

logger: logging.Logger = logging.getLogger(__name__)


class AtomRadiusBitSentences(BaseMolSentences):
    def get_structured_sentences(self, radii: list[int]) -> list[list[str]]:
        return [
            [
                str(self._atom_radius_bit_map.atom_radius_bit_dict[atom][r])
                for r in radii
                if r in self._atom_radius_bit_map.atom_radius_bit_dict[atom]
            ]
            for atom in self._atom_radius_bit_map.atoms
        ]


class AtomRadiusBitSentencesLoader(BaseMolSentencesSeriesLoader):
    def _gen_sentences_series_iter(
        self,
        atom_radius_bit_map_series_iter: SeriesWrapperIter,
        shuffle_index: list[int] | None = None,
    ) -> SeriesWrapperIter:
        return atom_radius_bit_map_series_iter.derive(AtomRadiusBitSentences)
