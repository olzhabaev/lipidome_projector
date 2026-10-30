"""Module concerning the testing of structure processing."""

import logging

from rdkit.Chem.rdchem import Mol

from lipid_vector_space.descriptors.atom_radius_bit_map import (
    AtomRadiusBitMap,
)


logger: logging.Logger = logging.getLogger(__name__)


def test_creation_success(picoline_mol: Mol) -> None:
    desc: AtomRadiusBitMap = AtomRadiusBitMap.from_mol(picoline_mol, 2, True)

    assert isinstance(desc.atom_radius_bit_dict[0][0], int)


def test_get_bit(picoline_fp_bit_desc: AtomRadiusBitMap) -> None:
    assert picoline_fp_bit_desc.atom_radius_bit_dict[1][1] == 98513984
    assert picoline_fp_bit_desc.atom_radius_bit_dict[2][1] == 98513984
    assert picoline_fp_bit_desc.atom_radius_bit_dict[5][2] == 4048591891
