"""Module concerning the description of lipids."""

import logging

from dataclasses import dataclass, fields
from typing import cast, ClassVar, Self

import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


# * SINGLE LIPID DESCRIPTIONS -------------------------------------------------


@dataclass(frozen=True)
class _MapperMixIn:
    col_name_map: ClassVar[dict[str, str]]

    @property
    def mapped_values(self) -> dict[str, str]:
        return {
            self.col_name_map[field.name]: getattr(self, field.name)
            for field in fields(self)
        }


@dataclass(frozen=True)
class LMSDLipid(_MapperMixIn):
    index: str
    name: str
    abbreviation: str
    category: str
    class_: str
    mass: float
    smiles: str

    index_col_name: ClassVar[str] = "LM_ID"
    name_col_name: ClassVar[str] = "NAME"
    abbreviation_col_name: ClassVar[str] = "ABBREVIATION"
    category_col_name: ClassVar[str] = "CATEGORY"
    class_col_name: ClassVar[str] = "MAIN_CLASS"
    mass_col_name: ClassVar[str] = "EXACT_MASS"
    smiles_col_name: ClassVar[str] = "SMILES"

    col_name_map: ClassVar[dict[str, str]] = {
        "index": index_col_name,
        "name": name_col_name,
        "abbreviation": abbreviation_col_name,
        "category": category_col_name,
        "class_": class_col_name,
        "mass": mass_col_name,
        "smiles": smiles_col_name,
    }

    col_dtypes: ClassVar[dict[str, str]] = {
        index_col_name: "string",
        name_col_name: "string",
        abbreviation_col_name: "string",
        category_col_name: "string",
        class_col_name: "string",
        mass_col_name: "float",
        smiles_col_name: "string",
    }


@dataclass(frozen=True)
class SLLipid(_MapperMixIn):
    index: str
    name: str
    mass: float
    smiles: str

    index_col_name: ClassVar[str] = "Lipid ID"
    name_col_name: ClassVar[str] = "Abbreviation*"
    mass_col_name: ClassVar[str] = "Mass (pH7.3)"
    smiles_col_name: ClassVar[str] = "SMILES (pH7.3)"

    col_name_map: ClassVar[dict[str, str]] = {
        "index": index_col_name,
        "name": name_col_name,
        "mass": mass_col_name,
        "smiles": smiles_col_name,
    }

    col_dtypes: ClassVar[dict[str, str]] = {
        index_col_name: "string",
        name_col_name: "string",
        mass_col_name: "float",
        smiles_col_name: "string",
    }


@dataclass(frozen=True)
class ParsedLipid(_MapperMixIn):
    original_name: str
    parsed_name: str

    level: str

    category: str
    class_: str
    species: str
    molecular_species: str
    sn_position: str
    structure_defined: str
    full_structure: str
    complete_structure: str

    fa1: str
    fa2: str
    fa3: str
    fa4: str
    lcb: str

    status: str = ""
    message: str = ""

    original_name_col_name: ClassVar[str] = "ORIGINAL_NAME"
    parsed_name_col_name: ClassVar[str] = "PARSED_NAME"
    level_col_name: ClassVar[str] = "LEVEL"
    category_col_name: ClassVar[str] = "CATEGORY"
    class_col_name: ClassVar[str] = "CLASS"
    species_col_name: ClassVar[str] = "SPECIES"
    molecular_species_col_name: ClassVar[str] = "MOLECULAR_SPECIES"
    sn_position_col_name: ClassVar[str] = "SN_POSITION"
    structure_defined_col_name: ClassVar[str] = "STRUCTURE_DEFINED"
    full_structure_col_name: ClassVar[str] = "FULL_STRUCTURE"
    complete_structure_col_name: ClassVar[str] = "COMPLETE_STRUCTURE"
    fa1_col_name: ClassVar[str] = "FA1"
    fa2_col_name: ClassVar[str] = "FA2"
    fa3_col_name: ClassVar[str] = "FA3"
    fa4_col_name: ClassVar[str] = "FA4"
    lcb_col_name: ClassVar[str] = "LCB"
    status_col_name: ClassVar[str] = "STATUS"
    message_col_name: ClassVar[str] = "MESSAGE"

    col_name_map: ClassVar[dict[str, str]] = {
        "original_name": original_name_col_name,
        "parsed_name": parsed_name_col_name,
        "level": level_col_name,
        "category": category_col_name,
        "class_": class_col_name,
        "species": species_col_name,
        "molecular_species": molecular_species_col_name,
        "sn_position": sn_position_col_name,
        "structure_defined": structure_defined_col_name,
        "full_structure": full_structure_col_name,
        "complete_structure": complete_structure_col_name,
        "fa1": fa1_col_name,
        "fa2": fa2_col_name,
        "fa3": fa3_col_name,
        "fa4": fa4_col_name,
        "lcb": lcb_col_name,
        "status": status_col_name,
        "message": message_col_name,
    }


@dataclass(frozen=True)
class LipidDescription:
    original_name: str
    parsed_lipid: ParsedLipid
    index: str | None = None
    lmsd_lipid: LMSDLipid | None = None
    lmsd_sp_parsed_lipid: ParsedLipid | None = None
    sl_lipid: SLLipid | None = None

    def __post_init__(self) -> None:
        self._chk_original_name()
        self._set_index_if_none()

    def _chk_original_name(self) -> None:
        if self.original_name != self.parsed_lipid.original_name:
            raise ValueError(
                "Original name does not match parsed lipid original name."
            )
        if self.lmsd_lipid is not None:
            if self.original_name != self.lmsd_lipid.name:
                raise ValueError(
                    "Original name does not match LMSD lipid name."
                )
        if self.sl_lipid is not None:
            if self.original_name != self.sl_lipid.name:
                raise ValueError(
                    "Original name does not match SwissLipids abbreviation."
                )

    def _set_index_if_none(self) -> None:
        if self.index is None:
            object.__setattr__(self, "index", "I_" + self.original_name)


# * GROUP DESCRIPTIONS --------------------------------------------------------


class LipidCollection:
    def __init__(self, lipid_list: list[LipidDescription]) -> None:
        self._lipid_list: list[LipidDescription] = lipid_list

    def __getitem__(self, index):
        return self._lipid_list[index]

    @property
    def lipid_list(self) -> list[LipidDescription]:
        return self._lipid_list

    @property
    def lmsd_lipid_list(self) -> list[LipidDescription]:
        return [
            lipid for lipid in self._lipid_list if lipid.lmsd_lipid is not None
        ]

    @property
    def sl_lipid_list(self) -> list[LipidDescription]:
        return [
            lipid for lipid in self._lipid_list if lipid.sl_lipid is not None
        ]

    def concat(self, others: list[Self]) -> Self:
        combined_collection: Self = type(self)(
            self._lipid_list
            + [lipid for lc in others for lipid in lc.lipid_list]
        )

        return combined_collection

    def to_original_name_series(self) -> pd.Series:
        return pd.Series(
            [lipid.original_name for lipid in self._lipid_list],
            dtype="string",
            index=[lipid.index for lipid in self._lipid_list],
        )

    def to_parsed_df(self) -> pd.DataFrame:
        parsed_df: pd.DataFrame = pd.DataFrame(
            [lipid.parsed_lipid.mapped_values for lipid in self._lipid_list],
            dtype="string",
            index=[lipid.index for lipid in self._lipid_list],
        )

        parsed_df.index = parsed_df.index.rename("INDEX").astype("string")

        return parsed_df

    def to_name_df(self) -> pd.DataFrame:
        name_df: pd.DataFrame = pd.DataFrame(
            [
                {
                    lipid.parsed_lipid.parsed_name_col_name: lipid.parsed_lipid.parsed_name,  # noqa: E501
                    lipid.parsed_lipid.original_name_col_name: lipid.original_name,  # noqa: E501
                }
                for lipid in self._lipid_list
            ],
            dtype="string",
            index=[lipid.index for lipid in self._lipid_list],
        )

        return name_df

    def to_lmsd_df(self) -> pd.DataFrame:
        lmsd_df: pd.DataFrame = (
            pd.DataFrame([lipid.lmsd_lipid for lipid in self.lmsd_lipid_list])
            .rename(LMSDLipid.col_name_map, axis="columns")
            .astype(LMSDLipid.col_dtypes)
            .set_index("LM_ID")
        )

        return lmsd_df

    def to_lmsd_original_name_series(self) -> pd.Series:
        return pd.Series(
            [
                lipid.original_name
                for lipid in self.lmsd_lipid_list
                if lipid.lmsd_lipid is not None
            ],
            dtype="string",
            index=[
                lipid.lmsd_lipid.index
                for lipid in self.lmsd_lipid_list
                if lipid.lmsd_lipid is not None
            ],
        )

    def to_lmsd_generic_parsed_df(self) -> pd.DataFrame:
        parsed_lmsd_df: pd.DataFrame = self.to_parsed_df().set_index(
            pd.Index(
                [
                    lipid.lmsd_lipid.index
                    for lipid in self.lmsd_lipid_list
                    if lipid.lmsd_lipid is not None
                ],
                name="INDEX",
                dtype="string",
            )
        )

        return parsed_lmsd_df

    def to_lmsd_sp_parsed_df(self) -> pd.DataFrame:
        parsed_df: pd.DataFrame = pd.DataFrame(
            [
                (
                    lipid.parsed_lipid.mapped_values
                    if lipid.parsed_lipid.parsed_name != ""
                    else cast(
                        ParsedLipid, lipid.lmsd_sp_parsed_lipid
                    ).mapped_values
                )
                for lipid in self._lipid_list
            ],
            dtype="string",
        )

        parsed_lmsd_df: pd.DataFrame = parsed_df.set_index(
            pd.Index(
                [
                    lipid.lmsd_lipid.index
                    for lipid in self.lmsd_lipid_list
                    if lipid.lmsd_lipid is not None
                ],
                name="INDEX",
                dtype="string",
            )
        )

        return parsed_lmsd_df

    def to_sl_df(self) -> pd.DataFrame:
        sl_df: pd.DataFrame = (
            pd.DataFrame(
                [
                    lipid.sl_lipid.mapped_values
                    for lipid in self.sl_lipid_list
                    if lipid.sl_lipid is not None
                ]
            )
            .rename(SLLipid.col_name_map, axis="columns")
            .astype(SLLipid.col_dtypes)
            .set_index("Lipid ID")
        )

        return sl_df

    def to_sl_original_name_series(self) -> pd.Series:
        return pd.Series(
            [
                lipid.original_name
                for lipid in self.sl_lipid_list
                if lipid.sl_lipid is not None
            ],
            dtype="string",
            index=[
                lipid.sl_lipid.index
                for lipid in self.sl_lipid_list
                if lipid.sl_lipid is not None
            ],
        )

    def to_sl_parsed_df(self) -> pd.DataFrame:
        parsed_sl_df: pd.DataFrame = self.to_parsed_df().set_index(
            pd.Index(
                [
                    lipid.sl_lipid.index
                    for lipid in self.sl_lipid_list
                    if lipid.sl_lipid is not None
                ],
                name="INDEX",
                dtype="string",
            )
        )

        return parsed_sl_df
