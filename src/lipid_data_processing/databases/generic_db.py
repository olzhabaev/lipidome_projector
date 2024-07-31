"""Module concerning the generic database class."""

import logging

from collections.abc import Generator
from pathlib import Path
from typing import Self

import pandas as pd

from lipid_data_processing.databases.base_db_classes import (
    Database,
    UnifiedDatabase,
)
from lipid_data_processing.notation.parsing import (
    ParsedDataset,
    parse_name_series,
)
from lipid_data_processing.structures.structure_conversion import (
    mols_from_smiles,
)
from lipid_data_processing.util.iteration_util import gen_pd_chunks


logger: logging.Logger = logging.getLogger(__name__)


class GenericDB(Database):
    def __init__(
        self,
        df: pd.DataFrame,
        name_col_name: str,
        smiles_col_name: str,
        mass_col_name: str,
    ) -> None:
        """Generic database wrapper.
        :param df: Database dataframe.
        :param name_col_name: Name column name.
        :param smiles_col_name: SMILES column name.
        :param mass_col_name: Mass column name.
        """
        self._name_col_name: str = name_col_name
        self._smiles_col_name: str = smiles_col_name
        self._mass_col_name: str = mass_col_name
        super().__init__(df)
        self._chk_input()

    @classmethod
    def from_source_file(
        cls,
        path: Path,
        name_col_name: str,
        smiles_col_name: str,
        mass_col_name: str,
        sep: str,
    ) -> Self:
        """Create generic database from source file.
        :param path: Path to source file.
        :param name_col_name: Name column name.
        :param smiles_col_name: SMILES column name.
        :param mass_col_name: Mass column name.
        :param sep: Separator.
        :return: Generic database.
        """
        logger.info(f"Read generic database from: '{path}'.")
        return cls(
            df=pd.read_csv(path, index_col=0, sep=sep),
            name_col_name=name_col_name,
            smiles_col_name=smiles_col_name,
            mass_col_name=mass_col_name,
        )

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def parse(self) -> ParsedDataset:
        """Parse generic database.
        :return: Parsed generic dataset.
        """
        return parse_name_series(self._df[self._name_col_name].fillna(""))

    def unify(self) -> UnifiedDatabase:
        """Unify generic database.
        :return: Unified generic database.
        """
        return UnifiedDatabase.from_parsed_ds(
            parsed_ds=self.parse(),
            mass=self._df[self._mass_col_name],
            smiles=self._df[self._smiles_col_name],
        )

    def gen_mol_chunks(
        self, num_chunks: int
    ) -> Generator[pd.Series, None, None]:
        """Generate chunks of rdkit molecule series.
        :param num_chunks: Number of chunks to generate.
        :return: Iterable of mol chunks.
        """
        smiles_chunk_gen: Generator[pd.Series, None, None] = gen_pd_chunks(
            self._df[self._smiles_col_name], num_chunks
        )

        return (
            mols_from_smiles(smiles_chunk, ignore_failure=True)
            for smiles_chunk in smiles_chunk_gen
        )

    def _chk_input(self) -> None:
        if self._name_col_name not in self.df.columns:
            raise ValueError(f"Name column {self._name_col_name} not found.")
        if self._smiles_col_name not in self.df.columns:
            raise ValueError(
                f"SMILES column {self._smiles_col_name} not found."
            )
        if self._mass_col_name not in self.df.columns:
            raise ValueError(f"Mass column {self._mass_col_name} not found.")
        if self.df.empty:
            raise ValueError("Empty dataframe.")
