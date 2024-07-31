"""Module concerning the database processing base class."""

import logging

from abc import ABC, abstractmethod
from pathlib import Path
from typing import cast

from lipid_data_processing.databases.base_db_classes import Database

from lipid_vector_space.util.structure_util import (
    standardize_and_write_mols_series,
)
from lipid_vector_space.util.io_util import (
    chk_dir_exists,
    chk_file_exists,
    chk_files_dont_exist,
)

logger: logging.Logger = logging.getLogger(__name__)


class BaseDBProcessor(ABC):
    def __init__(
        self,
        source_file_path: Path,
        output_dir_path: Path,
        canonize_mols: bool,
        uncharge_mols: bool,
        num_mol_chunks: int,
        mols_output_paths: list[Path] | None = None,
        smiles_output_path: Path | None = None,
        parsed_db_output_path: Path | None = None,
    ) -> None:
        self._source_file_path: Path = source_file_path
        self._output_dir_path: Path = output_dir_path
        self._canonize_mols: bool = canonize_mols
        self._uncharge_mols: bool = uncharge_mols
        self._num_mol_chunks: int = num_mol_chunks

        self._mols_output_paths: list[Path] = self._gen_mols_output_paths(
            mols_output_paths
        )
        self._smiles_output_path: Path = self._gen_smiles_output_path(
            smiles_output_path
        )
        self._parsed_db_output_path: Path = self._gen_parsed_db_output_path(
            parsed_db_output_path
        )

        self._chk_paths()

        self._db: Database = self._load_db()

    @property
    @abstractmethod
    def db_name(self) -> str: ...

    @property
    def mols_output_paths(self) -> list[Path]:
        return self._mols_output_paths

    @property
    def smiles_output_path(self) -> Path:
        return self._smiles_output_path

    @property
    def parsed_db_output_path(self) -> Path:
        return self._parsed_db_output_path

    def proc_and_write_structures(self) -> None:
        standardize_and_write_mols_series(
            self._db.gen_mol_chunks(self._num_mol_chunks),
            self._uncharge_mols,
            self._canonize_mols,
            cast(list[Path], self._mols_output_paths),
            cast(Path, self._smiles_output_path),
        )

    def parse_and_write(self) -> None:
        self._db.parse().df.to_csv(self._parsed_db_output_path)

    @abstractmethod
    def _load_db(self) -> Database: ...

    def _gen_mols_output_paths(
        self, mols_output_paths: list[Path] | None
    ) -> list[Path]:
        if mols_output_paths is not None:
            return mols_output_paths
        else:
            return [
                self._output_dir_path / f"{self.db_name}_mols_{i}.pkl"
                for i in range(self._num_mol_chunks)
            ]

    def _gen_smiles_output_path(self, smiles_output_path: Path | None) -> Path:
        if smiles_output_path is not None:
            return smiles_output_path
        else:
            return self._output_dir_path / f"{self.db_name}_smiles.csv"

    def _gen_parsed_db_output_path(self, path: Path | None) -> Path:
        if path is not None:
            return path
        else:
            return self._output_dir_path / f"{self.db_name}_parsed.csv"

    def _chk_paths(self) -> None:
        chk_file_exists(self._source_file_path)
        chk_dir_exists(self._output_dir_path)
        chk_files_dont_exist(
            [self._parsed_db_output_path, self._smiles_output_path]
            + self._mols_output_paths
        )
