"""Module concerning the RDKit based conversion of structure data."""

import logging

from typing import Literal

import pandas as pd

from rdkit import Chem
from rdkit.Chem.rdchem import Mol


logger: logging.Logger = logging.getLogger(__name__)


def mols_to_smiles(
    mols: pd.Series,
    canonical: bool = True,
    nan_handling: Literal["drop", "keepnan", "raise"] = "keepnan",
) -> pd.Series:
    """Generate SMILES from a series of Mol objects.
    :param mols: Series of Mol objects.
    :param canonical: Whether to generate canonical SMILES.
    :param nan_handling: How to handle NaN values. If "drop",
        NaN values are dropped. If "keepnan", NaN values are
        kept. If "raise", an exception is raised if NaN values
        are present.
    :return: Series of canonical SMILES.
    """

    if nan_handling == "drop":
        mols = mols.dropna()
    elif nan_handling == "raise":
        if mols.isna().any():
            raise ValueError("NaN values are present.")

    return (
        mols.apply(
            lambda mol: (
                Chem.MolToSmiles(mol, canonical=canonical)
                if pd.notna(mol)
                else mol
            )
        )
        .rename("canonical_smiles")
        .astype("string")
    )


def mols_to_canonical_mols(mols: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Generate 'canonical' Mol objects, such that
    the atom numbering corresponds to the order of atoms in
    the corresponding canonical SMILES string.
    :param mols: Series of Mol objects.
    :return: Series of 'canonical' Mol objects and a series
        of the corresponding canonical SMILES.
    """

    canonical_smiles: pd.Series = mols_to_smiles(mols, canonical=True)
    canonical_mols: pd.Series = mols_from_smiles(canonical_smiles, True)

    return canonical_mols, canonical_smiles


def smiles_to_canonical_mols_smiles(
    smiles: pd.Series, ignore_failure: bool
) -> tuple[pd.Series, pd.Series]:
    """Generate canonical SMILES from a series of SMILES.
    For this Mol objects are generated.
    :param smiles: Series of SMILES.
    :param ignore_failure: Whether to ignore failures.
    :return: Series of Mol objects and corresponding series of
        canonical SMILES.
    :raises: Exception if any SMILES string is invalid
        and ignore_failure is False.
    """

    return mols_to_canonical_mols(mols_from_smiles(smiles, ignore_failure))


def mols_from_smiles(smiles: pd.Series, ignore_failure: bool) -> pd.Series:
    """Generate Mol objects from a series of SMILES.
    :param smiles: SMILES series.
    :param ignore_failure: Whether to ignore failures.
    :return: Series of corresponding Mol objects.
    :raises: Exception if any SMILES string is invalid
        and ignore_failure is False.
    """

    return smiles.apply(mol_from_smiles, ignore_failure=ignore_failure).rename(
        "rdkit_mol"
    )


def mol_from_smiles(smiles: str, ignore_failure: bool) -> Mol | None:
    """Generate a Mol object from a SMILES string.
    :param smiles: SMILES string.
    :param ignore_failure: Whether to ignore failures.
    :return: Mol object.
    :raises: Exception if SMILES string is invalid and ignore_failure is False.
    """
    try:
        mol: Mol | None = Chem.MolFromSmiles(smiles)
    except Exception as e:
        if not ignore_failure:
            raise e
        else:
            mol = None

    if mol is None and not ignore_failure:
        raise ValueError(f"Invalid SMILES string: {smiles}")

    return mol
