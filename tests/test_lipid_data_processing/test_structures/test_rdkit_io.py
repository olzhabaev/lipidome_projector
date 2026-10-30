"""Module concerning the testing of the RDKit IO."""

import logging

import pandas as pd
import pytest

from rdkit import Chem

from lipid_data_processing.structures import structure_conversion


logger: logging.Logger = logging.getLogger(__name__)


def test_mols_to_smiles():
    mols: pd.Series = pd.Series(
        [Chem.MolFromSmiles("CCO"), Chem.MolFromSmiles("CCN")]
    )
    smiles: pd.Series = structure_conversion.mols_to_smiles(mols)

    pd.testing.assert_series_equal(
        pd.Series(["CCO", "CCN"], name="canonical_smiles", dtype="string"),
        smiles,
    )


def test_mols_to_smiles_nan_handling():
    mols: pd.Series = pd.Series([Chem.MolFromSmiles("CCO"), pd.NA])  # type: ignore  # noqa: E501
    smiles_drop: pd.Series = structure_conversion.mols_to_smiles(
        mols, nan_handling="drop"
    )
    pd.testing.assert_series_equal(
        pd.Series(["CCO"], name="canonical_smiles", dtype="string"),
        smiles_drop,
    )

    smiles_keep: pd.Series = structure_conversion.mols_to_smiles(
        mols, nan_handling="keepnan"
    )
    pd.testing.assert_series_equal(
        pd.Series(["CCO", pd.NA], name="canonical_smiles", dtype="string"),
        smiles_keep,
    )


def test_mols_to_smiles_canonical():
    mols: pd.Series = pd.Series([Chem.MolFromSmiles("OCC")])
    smiles: pd.Series = structure_conversion.mols_to_smiles(
        mols, canonical=True
    )
    pd.testing.assert_series_equal(
        pd.Series(["CCO"], name="canonical_smiles", dtype="string"), smiles
    )


def test_mols_to_smiles_raise_on_nan():
    mols: pd.Series = pd.Series([pd.NA])
    with pytest.raises(ValueError, match="NaN values are present."):
        structure_conversion.mols_to_smiles(mols, nan_handling="raise")


def test_mol_from_smiles_valid_input():
    smiles: str = "CCO"
    mol: Chem.rdchem.Mol = structure_conversion.mol_from_smiles(
        smiles, ignore_failure=True
    )
    assert isinstance(mol, Chem.rdchem.Mol)


def test_mol_from_smiles_invalid_input_ignore_failure():
    smiles: str = "invalid_smiles"
    mol: Chem.rdchem.Mol = structure_conversion.mol_from_smiles(
        smiles, ignore_failure=True
    )
    assert mol is None


def test_mol_from_smiles_invalid_input_raise_exception():
    smiles: str = "invalid_smiles"
    with pytest.raises(ValueError, match="Invalid SMILES string"):
        structure_conversion.mol_from_smiles(smiles, ignore_failure=False)


def test_mols_from_smiles_valid_input():
    smiles: pd.Series = pd.Series(["CCO", "CCN"])
    mols: pd.Series = structure_conversion.mols_from_smiles(
        smiles, ignore_failure=True
    )
    assert all(isinstance(mol, Chem.rdchem.Mol) for mol in mols)


def test_mols_from_smiles_invalid_input_ignore_failure():
    smiles: pd.Series = pd.Series(["invalid_smiles"])
    mols: pd.Series = structure_conversion.mols_from_smiles(
        smiles, ignore_failure=True
    )
    assert all(mol is None for mol in mols)


def test_mols_from_smiles_invalid_input_raise_exception():
    smiles: pd.Series = pd.Series(["invalid_smiles"])
    with pytest.raises(ValueError, match="Invalid SMILES string"):
        structure_conversion.mols_from_smiles(smiles, ignore_failure=False)
