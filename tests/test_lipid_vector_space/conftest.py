"""Module concerning test fixtures."""

import logging

import rdkit.Chem as Chem
import pytest

from rdkit.Chem.rdchem import Mol

from lipid_vector_space.descriptors.atom_radius_bit_map import (
    AtomRadiusBitMap,
)


logger: logging.Logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def picoline_smiles() -> str:
    return "c1cccnc1C"


@pytest.fixture(scope="session")
def picoline_mol(picoline_smiles: str) -> Mol:
    return Chem.MolFromSmiles(picoline_smiles)


@pytest.fixture(scope="session")
def picoline_fp_bit_desc(picoline_mol: Mol) -> AtomRadiusBitMap:
    return AtomRadiusBitMap.from_mol(picoline_mol, 2, True)
