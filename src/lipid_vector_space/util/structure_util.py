"""Module concerning molecule structure standardization."""

import logging

from collections.abc import Generator, Iterable
from pathlib import Path

import pandas as pd

from lipid_data_processing.structures.structure_conversion import (
    mols_to_canonical_mols,
    mols_to_smiles,
)
from lipid_data_processing.structures.structure_standardization import (
    uncharge_mols,
)

from lipid_vector_space.util.io_util import chk_files_dont_exist


logger: logging.Logger = logging.getLogger(__name__)


def standardize_and_write_mols_series(
    mols_series_iter: Iterable[pd.Series],
    uncharge: bool,
    canonize: bool,
    mols_paths: list[Path],
    smiles_path: Path,
) -> None:
    """Standardize and write iterable of molecule series.
    :param mols_series_iter: Iterable of molecule series.
    :param uncharge: Whether to uncharge the molecules.
    :param canonize: Whether to canonize the molecules.
    :param mols_paths: Paths to write the standardized molecules to.
    :param smiles_path: Path to write the standardized SMILES to.
    """
    chk_files_dont_exist(mols_paths)

    stanarized_tuples_gen: Generator[
        tuple[pd.Series, pd.Series], None, None
    ] = standardize_mols_series(mols_series_iter, uncharge, canonize)

    smiles_chunks: list[pd.Series] = []
    for (mols, smiles), path in zip(
        stanarized_tuples_gen, mols_paths, strict=True
    ):
        logger.info(f"Write standardized molecules series to: '{path}'")
        mols.to_pickle(path)
        smiles_chunks.append(smiles)

    logger.info(f"Write standardized SMILES series to: '{smiles_path}'")
    pd.concat(smiles_chunks).to_csv(smiles_path)


def standardize_mols_series(
    mols_series_iter: Iterable[pd.Series], uncharge: bool, canonize: bool
) -> Generator[tuple[pd.Series, pd.Series], None, None]:
    """Standardize iterable of molecule series.
    :param mols_series_iter: Iterable of molecule series.
    :param uncharge: Whether to uncharge the molecules.
    :param canonize: Whether to canonize the molecules.
    :return: Generator of standardized molecules and their
        SMILES representations.
    """
    return (
        standardize_mols(mols, uncharge, canonize) for mols in mols_series_iter
    )


def standardize_mols(
    mols: pd.Series, uncharge: bool, canonize: bool
) -> tuple[pd.Series, pd.Series]:
    """Standardize molecules.
    :param mols: Series of molecules.
    :param uncharge: Whether to uncharge the molecules.
    :param canonize: Whether to canonize the molecules.
    :return: Standardized molecules and their SMILES representations.
    """
    mols = mols.dropna()
    if uncharge:
        mols = uncharge_mols(mols)
        smiles: pd.Series = mols_to_smiles(mols)
    if canonize:
        mols, smiles = mols_to_canonical_mols(mols)
    return mols, smiles
