"""Module concerning the radius-atom-bit sentences descriptor."""

import logging

from lipid_vector_space.util.iteration_util import SeriesWrapperIter
from lipid_vector_space.bit2vec.base_sentences import (
    BaseMolSentences,
    BaseMolSentencesSeriesLoader,
)


logger: logging.Logger = logging.getLogger(__name__)


class RadiusAtomBitSentences(BaseMolSentences):
    def get_structured_sentences(self, radii: list[int]) -> list[list[str]]:
        return self.get_radius_atom_sentences(radii)


class RadiusAtomBitSentencesLoader(BaseMolSentencesSeriesLoader):
    def _gen_sentences_series_iter(
        self,
        atom_radius_bit_map_series_iter: SeriesWrapperIter,
        shuffle_index: list[int] | None = None,
    ) -> SeriesWrapperIter:
        return atom_radius_bit_map_series_iter.derive(RadiusAtomBitSentences)
