"""Module concerning the generic database processor class."""

import logging

from pathlib import Path
from typing import cast

from lipid_data_processing.databases.base_db_classes import Database
from lipid_data_processing.databases.generic_db import GenericDB
from lipid_vector_space.databases.base_db_processor import BaseDBProcessor


logger: logging.Logger = logging.getLogger(__name__)


class GenericDBProcessor(BaseDBProcessor):
    def __init__(
        self,
        source_file_path: Path,
        output_dir_path: Path,
        canonize_mols: bool,
        uncharge_mols: bool,
        num_mol_chunks: int,
        db_name: str,
        name_col_name: str,
        mass_col_name: str,
        smiles_col_name: str,
        sep: str,
        mols_output_paths: list[Path] | None = None,
        smiles_output_path: Path | None = None,
        unified_db_output_path: Path | None = None,
    ) -> None:
        self._name: str = db_name
        self._name_col_name: str = name_col_name
        self._mass_col_name: str = mass_col_name
        self._smiles_col_name: str = smiles_col_name
        self._sep: str = sep
        super().__init__(
            source_file_path=source_file_path,
            output_dir_path=output_dir_path,
            canonize_mols=canonize_mols,
            uncharge_mols=uncharge_mols,
            num_mol_chunks=num_mol_chunks,
            mols_output_paths=mols_output_paths,
            smiles_output_path=smiles_output_path,
            parsed_db_output_path=unified_db_output_path,
        )

    @property
    def db_name(self) -> str:
        return self._name

    def _load_db(self) -> Database:
        return GenericDB.from_source_file(
            path=self._source_file_path,
            name_col_name=cast(str, self._name_col_name),
            mass_col_name=cast(str, self._mass_col_name),
            smiles_col_name=cast(str, self._smiles_col_name),
            sep=cast(str, self._sep),
        )
