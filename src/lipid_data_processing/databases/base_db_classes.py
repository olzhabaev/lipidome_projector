"""Module concerning base database classes."""

import logging

from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Self

import pandas as pd

from lipid_data_processing.notation.parsing import ParsedDataset


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UnifiedDBColNames:
    index: str = "INDEX"

    original_name: str = "ORIGINAL_NAME"
    parsed_name: str = "PARSED_NAME"

    level: str = "LEVEL"

    category: str = "CATEGORY"
    class_: str = "CLASS"
    species: str = "SPECIES"
    molecular_species: str = "MOLECULAR_SPECIES"
    sn_position: str = "SN_POSITION"
    structure_defined: str = "STRUCTURE_DEFINED"
    full_structure: str = "FULL_STRUCTURE"
    complete_structure: str = "COMPLETE_STRUCTURE"

    fa1: str = "FA1"
    fa2: str = "FA2"
    fa3: str = "FA3"
    fa4: str = "FA4"

    lcb: str = "LCB"

    mass: str = "MASS"
    smiles: str = "SMILES"

    @property
    def col_names_list(self) -> list[str]:
        return list(getattr(self, field.name) for field in fields(self))

    @property
    def parsed_col_names_list(self) -> list[str]:
        return [
            self.original_name,
            self.parsed_name,
            self.level,
            self.category,
            self.class_,
            self.species,
            self.molecular_species,
            self.sn_position,
            self.structure_defined,
            self.full_structure,
            self.complete_structure,
            self.fa1,
            self.fa2,
            self.fa3,
            self.fa4,
            self.lcb,
        ]


class UnifiedDatabase:
    def __init__(
        self, df: pd.DataFrame, col_names: UnifiedDBColNames | None = None
    ):
        col_names = col_names if col_names is not None else UnifiedDBColNames()
        self._validate_df(df, col_names)
        self._df = df
        self._col_names = col_names

    @classmethod
    def from_parsed_ds(
        cls,
        parsed_ds: ParsedDataset,
        mass: pd.Series,
        smiles: pd.Series,
        col_names: UnifiedDBColNames | None = None,
    ) -> Self:
        """Create unified database from parsed dataset.
        :param parsed_ds: Parsed dataset.
        :param mass: Mass series.
        :param smiles: SMILES series.
        :param col_names: Column names.
        :return: Unified database.
        """
        cls._chk_indexes(mass, parsed_ds.df)
        cls._chk_indexes(smiles, parsed_ds.df)

        col_names = col_names if col_names is not None else UnifiedDBColNames()

        df: pd.DataFrame = pd.concat(
            [
                parsed_ds.df[col_names.parsed_col_names_list],
                pd.DataFrame(mass, columns=[col_names.mass]),
                pd.DataFrame(smiles, columns=[col_names.smiles]),
            ],
            axis="columns",
        )

        return cls(df)

    def concat(
        self,
        others: list["UnifiedDatabase"],
        drop_duplicates_col: str | None = None,
    ) -> "UnifiedDatabase":
        """Concat unified databases.
        :param others: List of other unified databases.
        :param drop_duplicates_col: Column to drop duplicates by.
        :return: Concatenated unified database.
        """

        concatenated_unified_df: pd.DataFrame = pd.concat(
            [self.df] + [ud.df for ud in others]
        )

        if drop_duplicates_col is not None:
            concatenated_unified_df = concatenated_unified_df.drop_duplicates(
                subset=drop_duplicates_col
            )

        return UnifiedDatabase(concatenated_unified_df)

    def get_subset(self, subset_index: pd.Index) -> Self:
        """Get subset of unified database.
        :param subset_index: Subset index.
        :return: Subset of unified database.
        """
        return type(self)(
            self.df.loc[subset_index.rename(self.col_names.index)],
            self.col_names,
        )

    @property
    def col_names(self) -> UnifiedDBColNames:
        return self._col_names

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @classmethod
    def _validate_df(
        cls, df: pd.DataFrame, col_names: UnifiedDBColNames
    ) -> None:
        if df.index.name != col_names.index:
            raise ValueError(
                f"Index name is {df.index.name}"
                f" but should be {col_names.index}"
            )

        missing_columns: set = set(col_names.col_names_list).difference(
            set(df.reset_index().columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing columns in dataframe: {missing_columns}"
            )

    @staticmethod
    def _chk_indexes(
        df1: pd.Series | pd.DataFrame, df2: pd.DataFrame | pd.DataFrame
    ) -> None:
        idx_sym_diff: pd.Index = df2.index.symmetric_difference(df1.index)
        if not idx_sym_diff.empty:
            raise ValueError(f"Indexes differ: {idx_sym_diff}")


class Database(ABC):
    def __init__(self, df: pd.DataFrame) -> None:
        self._df: pd.DataFrame = df

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @classmethod
    @abstractmethod
    def from_source_file(cls, source_file_path: Path, **kwargs) -> Self: ...

    @abstractmethod
    def parse(self, **kwargs) -> ParsedDataset: ...

    @abstractmethod
    def unify(self) -> UnifiedDatabase: ...

    @abstractmethod
    def gen_mol_chunks(
        self, num_chunks: int
    ) -> Generator[pd.Series, None, None]: ...
