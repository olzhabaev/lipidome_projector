"""Module concerning structure fixtures."""

import logging

import pandas as pd
import pytest

from rdkit import Chem


logger: logging.Logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def charged_mols_smiles() -> pd.Series:
    return pd.Series(
        [
            "C[NH3+]",
            "C[O-]",
            "O=C([O-])C[NH3+]",
        ]
    )


@pytest.fixture(scope="session")
def charged_mols(charged_mols_smiles: pd.Series) -> pd.Series:
    return charged_mols_smiles.apply(Chem.MolFromSmiles)


@pytest.fixture(scope="session")
def uncharged_mols_smiles() -> pd.Series:
    return pd.Series(
        [
            "CN",
            "CO",
            "O=C(O)CN",
        ]
    )
