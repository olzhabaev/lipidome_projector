"""Module concerning the covering random walks descriptor."""

import logging

from pathlib import Path
from random import choice
from typing import Self

from rdkit.Chem import Mol

from lipid_vector_space.descriptors.base_descriptor import (
    BaseDescriptor,
    BaseDescriptorWriter,
)


logger: logging.Logger = logging.getLogger(__name__)


class CoveringRandomWalks(BaseDescriptor):
    def __init__(self, walks: list[list[int]], atoms: list[int]) -> None:
        self._walks: list[list[int]] = walks
        self._atoms: list[int] = atoms

    @classmethod
    def from_mol(cls, mol: Mol, max_len: int) -> Self:
        adjacency_dict: dict[int, list[int]] = cls._gen_adjacency_dict(mol)
        random_walks: list[list[int]] = cls._get_random_walks(
            adjacency_dict, max_len
        )
        return cls(random_walks, list(adjacency_dict.keys()))

    @classmethod
    def deserialize(cls, data: dict) -> Self:
        return cls(data["walks"], data["atoms"])

    @property
    def atoms(self) -> list[int]:
        return self._atoms

    @property
    def walks(self) -> list[list[int]]:
        return self._walks

    def serialize(self) -> dict:
        return {"walks": self._walks, "atoms": self._atoms}

    @staticmethod
    def _gen_adjacency_dict(mol: Mol) -> dict[int, list[int]]:
        return {
            atom.GetIdx(): [
                neighbor.GetIdx() for neighbor in atom.GetNeighbors()
            ]
            for atom in mol.GetAtoms()  # type: ignore
        }

    @classmethod
    def _get_random_walks(
        cls, adjacency_dict: dict[int, list[int]], max_len: int
    ) -> list[list[int]]:
        atom_visit_counts: dict[int, int] = {
            atom: 0 for atom in adjacency_dict.keys()
        }
        random_walks: list[list[int]] = []

        while min(atom_visit_counts.values()) == 0:
            current_atom: int = cls._sample_least_visited_atom(
                atom_visit_counts
            )
            random_walk: list[int] = []
            while len(random_walk) < max_len:
                random_walk.append(current_atom)
                atom_visit_counts[current_atom] += 1
                neighbors_visit_counts: dict[int, int] = {
                    neighbor: atom_visit_counts[neighbor]
                    for neighbor in adjacency_dict[current_atom]
                    if neighbor not in random_walk
                }
                if len(neighbors_visit_counts) == 0:
                    break
                current_atom = cls._sample_least_visited_atom(
                    neighbors_visit_counts
                )
            random_walks.append(random_walk)

        return random_walks

    @staticmethod
    def _sample_least_visited_atom(atom_visit_counts: dict[int, int]) -> int:
        min_visit_count = min(atom_visit_counts.values())
        least_visited_atoms = [
            atom
            for atom, count in atom_visit_counts.items()
            if count == min_visit_count
        ]
        return choice(least_visited_atoms)


class CoveringRandomWalksWriter(BaseDescriptorWriter):
    def __init__(
        self,
        mols_paths: list[Path],
        output_dir_path: Path,
        max_len: int,
        file_suffix: str = "covering_random_walks",
    ) -> None:
        super().__init__(mols_paths, output_dir_path, file_suffix)
        self._max_len: int = max_len

    def _transform_mol(self, mol: Mol) -> dict:
        return CoveringRandomWalks.from_mol(mol, self._max_len).serialize()
