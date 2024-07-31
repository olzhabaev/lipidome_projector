"""Module concerning the atom radius bit map descriptor."""

import logging

from pathlib import Path
from typing import Self

from rdkit.Chem import AllChem, Mol

from lipid_vector_space.descriptors.base_descriptor import (
    BaseDescriptor,
    BaseDescriptorWriter,
)


logger: logging.Logger = logging.getLogger(__name__)


class AtomRadiusBitMap(BaseDescriptor):
    def __init__(self, atom_radius_bit_map: dict[int, dict[int, int]]) -> None:
        self._atom_radius_bit_dict: dict[int, dict[int, int]] = (
            atom_radius_bit_map
        )
        self._atoms: list[int] = list(self._atom_radius_bit_dict.keys())

    @classmethod
    def from_mol(
        cls, mol: Mol, max_radius: int, include_chirality: bool
    ) -> Self:
        """Instantiate bit info from RDKit Mol object.
        :param mol: RDKit Mol object.
        :param max_radius: Maximum radius.
        :param include_chirality: Whether to include chirality.
        """
        return cls(
            cls._gen_atom_radius_bit_dict(
                mol, cls._gen_bit_info_map(mol, max_radius, include_chirality)
            )
        )

    @classmethod
    def deserialize(
        cls, atom_radius_bit_dict: dict[int, dict[int, int]]
    ) -> Self:
        return cls(atom_radius_bit_dict)

    @property
    def atoms(self) -> list[int]:
        return self._atoms

    @property
    def atom_radius_bit_dict(self) -> dict[int, dict[int, int]]:
        return self._atom_radius_bit_dict

    def serialize(self) -> dict[int, dict[int, int]]:
        return self._atom_radius_bit_dict

    @staticmethod
    def _gen_bit_info_map(
        mol: Mol, radius: int, include_chirality: bool
    ) -> dict[int, tuple[tuple[int, int], ...]]:
        ao = AllChem.AdditionalOutput()
        ao.CollectBitInfoMap()
        AllChem.GetMorganGenerator(  # type: ignore
            radius=radius, includeChirality=include_chirality
        ).GetSparseCountFingerprint(mol, additionalOutput=ao)
        bit_info_map: dict = ao.GetBitInfoMap()

        return bit_info_map

    @staticmethod
    def _gen_atom_radius_bit_dict(
        mol: Mol, bit_info: dict[int, tuple[tuple[int, int], ...]]
    ) -> dict[int, dict[int, int]]:
        atom_radius_bit_dict: dict[int, dict[int, int]] = {
            atom.GetIdx(): {} for atom in mol.GetAtoms()  # type: ignore
        }

        for bit, info in bit_info.items():
            for atom, radius in info:
                atom_radius_bit_dict[atom][radius] = bit

        return atom_radius_bit_dict


class AtomRadiusBitMapWriter(BaseDescriptorWriter):
    def __init__(
        self,
        mols_paths: list[Path],
        output_dir_path: Path,
        max_radius: int,
        include_chirality: bool,
        file_suffix: str = "atom_radius_bit_map",
    ) -> None:
        super().__init__(mols_paths, output_dir_path, file_suffix)
        self._max_radius: int = max_radius
        self._include_chirality: bool = include_chirality

    def _transform_mol(self, mol: Mol) -> dict:
        return AtomRadiusBitMap.from_mol(
            mol, self._max_radius, self._include_chirality
        ).serialize()
