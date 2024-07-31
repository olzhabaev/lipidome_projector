"""Module concerning special column names."""

import logging

from dataclasses import dataclass


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LipidomeColNames:
    lipidome: str = "LIPIDOME"
    abundance: str = "ABUNDANCE"
    color: str = "COLOR"
    row_id: str = "ROW_ID"


@dataclass(frozen=True)
class LipidFeaturesColNames:
    lipid: str = "LIPID"
    lipid_category: str = "CATEGORY"
    lipid_class: str = "CLASS"
    smiles: str = "SMILES"


@dataclass(frozen=True)
class VecSpaceColNames:
    vec_space_2d_1: str = "t-SNE 1 (2D)"
    vec_space_2d_2: str = "t-SNE 2 (2D)"
    vec_space_3d_1: str = "t-SNE 1 (3D)"
    vec_space_3d_2: str = "t-SNE 2 (3D)"
    vec_space_3d_3: str = "t-SNE 3 (3D)"

    @property
    def vec_space_2d(self) -> tuple[str, str]:
        return (self.vec_space_2d_1, self.vec_space_2d_2)

    @property
    def vec_space_3d(self) -> tuple[str, str, str]:
        return (self.vec_space_3d_1, self.vec_space_3d_2, self.vec_space_3d_3)

    @property
    def vec_space_full(self) -> tuple[str, str, str, str, str]:
        return (
            self.vec_space_2d_1,
            self.vec_space_2d_2,
            self.vec_space_3d_1,
            self.vec_space_3d_2,
            self.vec_space_3d_3,
        )


@dataclass(frozen=True)
class ChangeColNames:
    change: str = "CHANGE"
    from_lipidome: str = "FROM"
    to_lipidome: str = "TO"


@dataclass(frozen=True)
class ColNames(
    LipidomeColNames,
    LipidFeaturesColNames,
    VecSpaceColNames,
    ChangeColNames,
):
    pass
