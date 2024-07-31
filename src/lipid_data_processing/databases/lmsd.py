"""Module concerning the Lipid Maps Structure Database."""

import logging

from collections.abc import Generator
from csv import QUOTE_ALL
from pathlib import Path
from typing import Literal, Self

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
from lipid_data_processing.structures.structure_io import sdf_to_df
from lipid_data_processing.util.iteration_util import gen_pd_chunks


logger: logging.Logger = logging.getLogger(__name__)


_CAT_MAP: dict[str, str] = {
    "Fatty Acyls [FA]": "FA",
    "Glycerolipids [GL]": "GL",
    "Glycerophospholipids [GP]": "GP",
    "Sphingolipids [SP]": "SP",
    "Sterol Lipids [ST]": "ST",
    "Prenol Lipids [PR]": "PR",
    "Saccharolipids [SL]": "SL",
    "Polyketides [PK]": "PK",
}


class UnifiedLMSD(UnifiedDatabase):
    @classmethod
    def from_source_data(
        cls,
        lmsd_df: pd.DataFrame,
        lmsd_parsed_ds: ParsedDataset,
        col_names: UnifiedDBColNames | None = None,
    ) -> Self:
        cls._chk_indexes(lmsd_df, lmsd_parsed_ds.df)
        return cls(cls._unify_lmsd(lmsd_df, lmsd_parsed_ds.df, col_names))

    @classmethod
    def _unify_lmsd(
        cls,
        lmsd_df: pd.DataFrame,
        lmsd_parsed_df: pd.DataFrame,
        col_names: UnifiedDBColNames | None,
    ) -> pd.DataFrame:
        col_names = col_names if col_names is not None else UnifiedDBColNames()

        unified_df: pd.DataFrame = pd.concat(
            [
                lmsd_parsed_df[col_names.parsed_col_names_list],
                lmsd_df[["EXACT_MASS", "SMILES"]].rename(
                    columns={
                        "EXACT_MASS": col_names.mass,
                        "SMILES": col_names.smiles,
                    }
                ),
            ],
            axis="columns",
        )

        unified_df[col_names.category] = lmsd_df["CATEGORY"].map(_CAT_MAP)
        unified_df.index.name = col_names.index

        return unified_df


class LMSD(Database):
    _DTYPES: dict[str, Literal["string", "float", "object"]] = {
        "LM_ID": "string",
        "NAME": "string",
        "SYSTEMATIC_NAME": "string",
        "CATEGORY": "string",
        "MAIN_CLASS": "string",
        "EXACT_MASS": "float",
        "FORMULA": "string",
        "INCHI_KEY": "string",
        "INCHI": "string",
        "SMILES": "string",
        "ABBREVIATION": "string",
        "SYNONYMS": "string",
        "PUBCHEM_CID": "string",
        "CHEBI_ID": "string",
        "KEGG_ID": "string",
        "HMDB_ID": "string",
        "SWISSLIPIDS_ID": "string",
        "SUB_CLASS": "string",
        "LIPIDBANK_ID": "string",
        "PLANTFA_ID": "string",
        "CLASS_LEVEL4": "string",
    }

    @classmethod
    def from_source_file(cls, path: Path, add_rdkit_data: bool) -> Self:
        """Create a LMSD database from a path to a source file.
        :param path: Path to the LMSD SDF / CSV file.
        :param add_rdkit_data: Whether to add RDKit Mol objects and SMILES.
        :return: LMSD database.
        :raises ValueError: If the file format is not supported.
        """
        if path.suffix == ".sdf":
            return cls.from_sdf(path, add_rdkit_data)
        elif path.suffix == ".csv":
            return cls.from_csv(path, add_rdkit_data)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}.")

    @classmethod
    def from_csv(cls, path: Path, add_rdkit_data: bool = False) -> Self:
        """Create a LMSD database from a CSV file.
        :param path: Path to the LMSD CSV file.
        :param add_rdkit_data: Whether to add RDKit Mol objects and SMILES.
        :return: LMSD database.
        """
        logger.info(f"Read LMSD CSV file: {path}.")

        lmsd_df: pd.DataFrame = pd.read_csv(
            path,
            sep=",",
            index_col="LM_ID",
            dtype=cls._DTYPES,
            quoting=QUOTE_ALL,
        )

        if add_rdkit_data:
            (
                lmsd_df["rdkit_mol"],
                lmsd_df["rdkit_smiles"],
            ) = smiles_to_canonical_mols_smiles(
                lmsd_df["SMILES"].fillna(""), ignore_failure=True
            )

        return cls(lmsd_df)

    @classmethod
    def from_sdf(cls, path: Path, add_rdkit_data: bool = False) -> Self:
        """Create a LMSD database from a SDF file.
        :param path: Path to the LMSD SDF file.
        :param add_rdkit_data: Whether to add RDKit Mol objects and SMILES.
        :return: LMSD database.
        """
        logger.info(f"Read LMSD SDF file: {path}.")

        lmsd_df: pd.DataFrame = sdf_to_df(path, add_rdkit_data)
        lmsd_df = lmsd_df.astype(
            {
                key: dtype
                for key, dtype in cls._DTYPES.items()
                if key in lmsd_df.columns
            }
        ).set_index("LM_ID")

        return cls(lmsd_df)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def parse(
        self,
        add_failures_parsed_species: bool = True,
        add_categories_to_unparsed: bool = True,
    ) -> ParsedDataset:
        """Parse the shorthand notation of the LMSD database.
        :param lmsd_df: LMSD dataframe.
        :param add_failures_parsed_species: Whether to parse on
            species level for name parsing failures.
        :param add_categories_to_unparsed: Whether to add the
            category information to unparsed lipids.
        :return: Dataset containing the parsed abbreviations and
            additional information.
        """
        parsed_ds: ParsedDataset = parse_name_series(
            self._df["NAME"].fillna("")
        )
        parsed_df: pd.DataFrame = parsed_ds.df.copy()

        if add_failures_parsed_species and not parsed_ds.failure_index.empty:
            parsed_df.update(
                parse_name_series(
                    self._df.loc[parsed_ds.failure_index][
                        "ABBREVIATION"
                    ].dropna()
                ).success_ds.df
            )
            parsed_df.update(
                self.df["NAME"].rename(parsed_ds.col_names.original_name)
            )

        if add_categories_to_unparsed:
            parsed_df.update(
                self._df[
                    (parsed_df["CATEGORY"] == "UNDEFINED")
                    | (parsed_df["CATEGORY"] == "")
                ]["CATEGORY"]
                .apply(lambda category: _CAT_MAP.get(category, "UNDEFINED"))
                .rename(parsed_ds.col_names.category)
            )

        return ParsedDataset(parsed_df, parsed_ds.col_names)

    def unify(self) -> UnifiedLMSD:
        """Unify the LMSD database.
        :return: Unified LMSD database.
        """
        return UnifiedLMSD.from_source_data(self._df, self.parse())

    def gen_mol_chunks(
        self, num_chunks: int
    ) -> Generator[pd.Series, None, None]:
        """Generate chunks of rdkit molecule series to limit memory usage.
        :param num_chunks: Number of chunks to generate.
        :return: Generator of mol chunks.
        """
        if "rdkit_mol" in self.df.columns:
            return gen_pd_chunks(self.df["rdkit_mol"], num_chunks)
        else:
            smiles_chunk_gen: Generator[pd.Series, None, None] = gen_pd_chunks(
                self._df["SMILES"], num_chunks
            )
            return (
                mols_from_smiles(smiles_chunk, ignore_failure=True)
                for smiles_chunk in smiles_chunk_gen
            )
