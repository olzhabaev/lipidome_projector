"""Module concerning the SwissLipids database."""

import logging

from collections.abc import Generator
from pathlib import Path
from typing import Self

import pandas as pd

from lipid_data_processing.databases.base_db_classes import (
    Database,
    UnifiedDatabase,
    UnifiedDBColNames,
)
from lipid_data_processing.notation.parsing import (
    ParsedDataset,
    parse_name_series,
)
from lipid_data_processing.structures.structure_conversion import (
    mols_from_smiles,
    smiles_to_canonical_mols_smiles,
)
from lipid_data_processing.util.iteration_util import gen_pd_chunks


logger: logging.Logger = logging.getLogger(__name__)


class UnifiedSL(UnifiedDatabase):
    @classmethod
    def from_source_data(
        cls,
        sl_df: pd.DataFrame,
        sl_parsed_ds: ParsedDataset,
        col_names: UnifiedDBColNames | None = None,
    ) -> Self:
        cls._chk_indexes(sl_df, sl_parsed_ds.df)
        return cls(cls._unify_sl(sl_df, sl_parsed_ds, col_names))

    @classmethod
    def _unify_sl(
        cls,
        sl_df: pd.DataFrame,
        sl_parsed_ds: ParsedDataset,
        col_names: UnifiedDBColNames | None,
    ) -> pd.DataFrame:
        col_names = col_names if col_names is not None else UnifiedDBColNames()

        unified_df: pd.DataFrame = pd.concat(
            [
                sl_parsed_ds.df[col_names.parsed_col_names_list],
                sl_df[["Mass (pH7.3)", "SMILES (pH7.3)"]].rename(
                    columns={
                        "Mass (pH7.3)": col_names.mass,
                        "SMILES (pH7.3)": col_names.smiles,
                    }
                ),
            ],
            axis="columns",
        )

        unified_df.index.name = col_names.index

        return unified_df


class SwissLipids(Database):
    _SL_DTYPES: dict = {
        "Lipid ID": "string",
        "Level": "string",
        "Name": "string",
        "Abbreviation*": "string",
        "Synonyms*": "string",
        "Lipid class*": "string",
        "Parent": "string",
        "Components*": "string",
        "SMILES (pH7.3)": "string",
        "InChI (pH7.3)": "string",
        "InChI key (pH7.3)": "string",
        "Formula (pH7.3)": "string",
        "Charge (pH7.3)": "float",
        "Mass (pH7.3)": "float",
        "Exact Mass (neutral form)": "float",
        "Exact m/z of [M.]+": "float",
        "Exact m/z of [M+H]+": "float",
        "Exact m/z of [M+K]+": "float",
        "Exact m/z of [M+Na]+": "float",
        "Exact m/z of [M+Li]+": "float",
        "Exact m/z of [M+NH4]+": "float",
        "Exact m/z of [M-H]-": "float",
        "Exact m/z of [M+Cl]-": "float",
        "Exact m/z of [M+OAc]-": "float",
        "CHEBI": "string",
        "LIPID MAPS": "string",
        "HMDB": "string",
        "MetaNetX": "string",
        "PMID": "string",
    }

    @classmethod
    def from_source_file(
        cls,
        path: Path,
        drop_non_isomers: bool,
        add_rdkit_data: bool = False,
    ) -> Self:
        """Create a SwissLipids database from a path to a TSV file.
        :param path: Path to the SwissLipids TSV file.
        :param drop_non_isomers: Whether to drop non-isomers.
        :param add_rdkit_data: Whether to add rdkit molecule
            object & SMILES to dataframe.
        :return: SwissLipids database.
        """
        logger.info(f"Read SwissLipids TSV file: {path}.")

        df: pd.DataFrame = pd.read_csv(
            path,
            sep="\t",
            encoding="ISO-8859-1",
            index_col="Lipid ID",
            dtype=cls._SL_DTYPES,
        )

        if drop_non_isomers:
            df = df[df["Level"] == "Isomeric subspecies"]

        if add_rdkit_data:
            (df["rdkit_mol"], df["rdkit_smiles"]) = (
                smiles_to_canonical_mols_smiles(
                    df["SMILES"].fillna(""), ignore_failure=True
                )
            )

        return cls(df)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def parse(self) -> ParsedDataset:
        """Parse SwissLipids database.
        :return: Parsed SwissLipids dataset.
        """
        abbreviations_frame: pd.DataFrame = pd.DataFrame(
            self._df["Abbreviation*"]
            .fillna("")
            .apply(
                lambda abbreviation_str: {
                    "abbreviation_" + str(i): abbreviation
                    for i, abbreviation in enumerate(
                        abbreviation_str.split("|")
                    )
                }
            )
            .to_list(),
            index=self._df.index,
        )

        # TODO Handle parsing and validation of abbreviation
        # alternatives.
        parsed_ds: ParsedDataset = parse_name_series(
            abbreviations_frame["abbreviation_0"]
        )

        return parsed_ds

    def unify(self) -> UnifiedSL:
        """Unify SwissLipids database.
        :return: Unified SwissLipids database.
        """
        return UnifiedSL.from_source_data(self._df, self.parse())

    def gen_mol_chunks(
        self, num_chunks: int
    ) -> Generator[pd.Series, None, None]:
        """Generate chunks of rdkit molecule series to reduce memory usage.
        :param num_chunks: Number of chunks to generate.
        :return: Iterable of mol chunks.
        """
        smiles_chunk_gen: Generator[pd.Series, None, None] = gen_pd_chunks(
            self._df["SMILES (pH7.3)"], num_chunks
        )

        return (
            mols_from_smiles(smiles_chunk, ignore_failure=True)
            for smiles_chunk in smiles_chunk_gen
        )
