"""Module concerning base descritpor classes."""

import logging

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Self

from rdkit.Chem import Mol

from lipid_vector_space.util.iteration_util import SeriesWrapperIter
from lipid_vector_space.util.io_util import (
    chk_dir_exists,
    chk_files_exist,
    chk_files_dont_exist,
    SeriesFromFilesGenerator,
    write_series_iter_to_files,
)


logger: logging.Logger = logging.getLogger(__name__)


class BaseDescriptor(ABC):
    @classmethod
    @abstractmethod
    def from_mol(cls, mol: Mol, **kwargs: dict[str, Any]) -> Self: ...

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict) -> Self: ...

    @property
    @abstractmethod
    def atoms(self) -> list[int]: ...

    @abstractmethod
    def serialize(self) -> dict: ...


class BaseDescriptorWriter(ABC):
    def __init__(
        self,
        mols_paths: list[Path],
        output_dir_path: Path,
        file_suffix: str,
    ) -> None:
        self._mols_paths: list[Path] = mols_paths
        self._output_dir_path: Path = output_dir_path
        self._file_suffix: str = file_suffix
        self._output_paths: list[Path] = self._gen_output_paths()
        self._mols_iter: SeriesWrapperIter = self._gen_mols_iter()
        self._chk_paths()

    def __call__(self) -> None:
        write_series_iter_to_files(
            self._mols_iter.derive(self._transform_mol).to_series_iter(),
            self._output_paths,
        )

    @property
    def output_paths(self) -> list[Path]:
        return self._output_paths

    @abstractmethod
    def _transform_mol(self, mol: Mol) -> dict: ...

    def _chk_paths(self) -> None:
        chk_dir_exists(self._output_dir_path)
        chk_files_exist(self._mols_paths)
        chk_files_dont_exist(self._output_paths)

    def _gen_output_paths(self) -> list[Path]:
        return [
            self._output_dir_path / f"{mol_input.stem}_{self._file_suffix}.pkl"
            for mol_input in self._mols_paths
        ]

    def _gen_mols_iter(self) -> SeriesWrapperIter:
        return SeriesWrapperIter.from_series_iter(
            SeriesFromFilesGenerator(self._mols_paths)
        )
