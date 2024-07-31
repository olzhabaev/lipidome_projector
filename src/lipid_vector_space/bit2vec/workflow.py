"""Module concerning the bit2vec workflow."""

import logging

from pathlib import Path
from typing import Any, cast, Literal

from lipid_vector_space.bit2vec.atom_radius_bit_sentences import (
    AtomRadiusBitSentencesLoader,
)
from lipid_vector_space.bit2vec.random_walk_sentences import (  # noqa: E501
    RandomWalkSentencesLoader,
)
from lipid_vector_space.bit2vec.radius_atom_bit_sentences import (
    RadiusAtomBitSentencesLoader,
)
from lipid_vector_space.bit2vec.input import (
    BaseMolSentencesSeriesLoader,
    BaseInput,
    D2VTrainingInput,
    InputChain,
    W2VTrainingInput,
    W2VCompositionInput,
)
from lipid_vector_space.bit2vec.d2v_embedding import (
    Doc2VecEmbedding,
)
from lipid_vector_space.bit2vec.w2v_embedding import (
    Word2VecEmbedding,
)
from lipid_vector_space.util.io_util import (
    chk_dir_exists,
    chk_files_exist,
    chk_file_doesnt_exist,
)


logger: logging.Logger = logging.getLogger(__name__)


ORDERING_OPTIONS = Literal["radius_atom", "atom_radius", "rw"]
MODEL_OPTIONS = Literal["w2v", "d2v"]


class L2VModel:
    def __init__(
        self,
        output_dir_path: Path,
        model: MODEL_OPTIONS,
        orderings: list[ORDERING_OPTIONS],
        radii: list[int],
        model_params: dict[str, Any],
        shuffle: bool,
        atom_radius_bit_map_paths: list[Path],
        random_walks_paths: list[Path] | None = None,
    ) -> None:
        self._output_dir_path: Path = output_dir_path
        self._model: MODEL_OPTIONS = model
        self._orderings: list[ORDERING_OPTIONS] = orderings
        self._radii: list[int] = radii
        self._model_params: dict[str, Any] = model_params
        self._shuffle: bool = shuffle
        self._atom_radius_bit_map_paths: list[Path] = atom_radius_bit_map_paths
        self._random_walks_paths: list[Path] | None = random_walks_paths

        self._vec_path: Path = self._gen_vec_path()
        self._sub_vec_path: Path | None = self._gen_sub_vec_path()
        self._model_path: Path = self._gen_model_path()
        self._sentences_loaders: list[BaseMolSentencesSeriesLoader] = (
            self._get_sentences_loaders()
        )
        self._training_input: BaseInput = self._get_training_input()
        self._composition_input: BaseInput | None = (
            self._get_composition_input()
        )

        self._chk_paths()

    def __call__(self) -> None:
        match self._model:
            case "w2v":
                Word2VecEmbedding.with_training(
                    training_data=self._training_input,
                    model_params=self._model_params,
                    composition_data=cast(BaseInput, self._composition_input),
                ).save(
                    vec_path=self._vec_path,
                    sub_vec_path=cast(Path, self._sub_vec_path),
                    model_path=self._model_path,
                )
            case "d2v":
                Doc2VecEmbedding.with_training(
                    training_data=self._training_input,
                    model_params=self._model_params,
                ).save(
                    vec_path=self._vec_path,
                    model_path=self._model_path,
                )
            case _:
                raise ValueError(f"Invalid model: {self._model}")

    @property
    def vec_path(self) -> Path:
        return self._vec_path

    def _chk_paths(self) -> None:
        chk_dir_exists(self._output_dir_path)
        chk_files_exist(self._atom_radius_bit_map_paths)
        if self._random_walks_paths is not None:
            chk_files_exist(self._random_walks_paths)
        chk_file_doesnt_exist(self._vec_path)
        if self._sub_vec_path is not None:
            chk_file_doesnt_exist(self._sub_vec_path)
        chk_file_doesnt_exist(self._model_path)

    def _chk_model_params(self) -> None:
        if "rw" in self._orderings and self._random_walks_paths is None:
            raise ValueError(
                "Random walk ordering requires random walk paths."
            )
        if (
            "rw" not in self._orderings
            and self._random_walks_paths is not None
        ):
            raise ValueError(
                "Non-random walk ordering does not require random walk paths."
            )

    def _gen_vec_path(self) -> Path:
        return self._output_dir_path / f"{self._model}_vectors.csv"

    def _gen_sub_vec_path(self) -> Path | None:
        match self._model:
            case "w2v":
                return self._output_dir_path / f"{self._model}_sub_vectors.csv"
            case _:
                return None

    def _gen_model_path(self) -> Path:
        return self._output_dir_path / f"{self._model}.gz"

    def _get_sentences_loaders(self) -> list[BaseMolSentencesSeriesLoader]:
        return [
            self._get_sentences_loader(ordering)
            for ordering in self._orderings
        ]

    def _get_sentences_loader(
        self, ordering: ORDERING_OPTIONS
    ) -> BaseMolSentencesSeriesLoader:
        match ordering:
            case "radius_atom":
                return RadiusAtomBitSentencesLoader(
                    self._atom_radius_bit_map_paths, self._shuffle
                )
            case "atom_radius":
                return AtomRadiusBitSentencesLoader(
                    self._atom_radius_bit_map_paths, self._shuffle
                )
            case "rw":
                return RandomWalkSentencesLoader(
                    self._atom_radius_bit_map_paths,
                    cast(list[Path], self._random_walks_paths),
                    self._shuffle,
                )
            case _:
                raise ValueError(f"Invalid ordering: {ordering}")

    def _get_training_input(self) -> BaseInput:
        match self._model:
            case "w2v":
                return InputChain(
                    [
                        W2VTrainingInput(sentences_loader, self._radii)
                        for sentences_loader in self._sentences_loaders
                    ]
                )
            case "d2v":
                return InputChain(
                    [
                        D2VTrainingInput(sentences_loader, self._radii)
                        for sentences_loader in self._sentences_loaders
                    ]
                )
            case _:
                raise ValueError(f"Invalid model: {self._model}")

    def _get_composition_input(self) -> BaseInput | None:
        match self._model:
            case "w2v":
                return W2VCompositionInput(
                    AtomRadiusBitSentencesLoader(
                        self._atom_radius_bit_map_paths, shuffle=False
                    ),
                    self._radii,
                )
            case _:
                return None
