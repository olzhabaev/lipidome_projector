""" """

import logging

from dataclasses import asdict, dataclass, field, fields
from typing import ClassVar, Literal, Self

logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GridHeaders:
    abundance: str = "ABUNDANCE"
    features: str = "FEATURES"
    lipid: str = "LIPID"
    vecs: str = "VECTORS"
    change: str = "CHANGE"


@dataclass(frozen=True)
class GridData:
    records: list[dict] = field(default_factory=list)
    virtual_records: list[dict] = field(default_factory=list)
    col_groups_defs: list[dict] = field(default_factory=list)
    selected_rows: list[dict] = field(default_factory=list)

    _COMMON_COL_DEF_PARAMS: ClassVar[dict] = {
        "filter": True,
        "floatingFilter": True,
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "sortable": True,
    }

    @classmethod
    def from_dict(cls, input_dict: dict) -> Self:
        return cls(**input_dict)

    def __post_init__(self) -> None:
        for field_ in fields(self):
            if getattr(self, field_.name) is None:
                object.__setattr__(self, field_.name, list())

    def get_filter(
        self, filter_by: Literal["virtual", "selected"], key: str
    ) -> list[str]:
        if filter_by == "virtual":
            records: list[dict] = self.virtual_records
        elif filter_by == "selected":
            records: list[dict] = self.selected_rows
        else:
            raise ValueError(f"Invalid filter_by value: {filter_by}")

        return [record[key] for record in records]

    def serialize(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class LipidomeData(GridData):
    @classmethod
    def from_serialized(
        cls,
        records: list[dict],
        feature_col_names: list[str],
        abundance_col_names: list[str],
        lipidome_col_name: str,
        color_col_name: str,
        feature_header: str,
        abundance_header: str,
    ) -> Self:
        return cls(
            records=records,
            col_groups_defs=cls._gen_col_group_defs(
                feature_col_names,
                abundance_col_names,
                lipidome_col_name,
                color_col_name,
                feature_header,
                abundance_header,
            ),
        )

    @classmethod
    def _gen_col_group_defs(
        cls,
        feature_col_names: list[str],
        abundance_col_names: list[str],
        lipidome_col_name: str,
        color_col_name: str,
        feature_header: str,
        abundance_header: str,
    ) -> list[dict]:
        return [
            {
                "headerName": feature_header,
                "children": cls._gen_feature_col_defs(
                    color_col_name, lipidome_col_name, feature_col_names
                ),
                "openByDefault": True,
            },
            {
                "headerName": abundance_header,
                "children": cls._gen_abundance_col_defs(abundance_col_names),
            },
        ]

    @classmethod
    def _gen_feature_col_defs(
        cls,
        color_col_name: str,
        lipidome_col_name: str,
        feature_col_names: list[str],
    ) -> list[dict]:
        lipidome_col_def: dict = cls._COMMON_COL_DEF_PARAMS | {
            "field": lipidome_col_name,
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
            "headerCheckboxSelectionFilteredOnly": True,
        }

        color_col_def: dict = cls._COMMON_COL_DEF_PARAMS | {
            "field": color_col_name,
            "columnGroupShow": "open",
            "cellStyle": {
                "function": "params.value && {'backgroundColor': params.value}"
            },
        }

        features_col_defs: list[dict] = [
            cls._COMMON_COL_DEF_PARAMS
            | {"field": col_name, "columnGroupShow": "open"}
            for col_name in feature_col_names
            if col_name != lipidome_col_name and col_name != color_col_name
        ]

        return [lipidome_col_def, color_col_def] + features_col_defs

    @classmethod
    def _gen_abundance_col_defs(
        cls, abundance_col_names: list[str]
    ) -> list[dict]:
        return [
            cls._COMMON_COL_DEF_PARAMS
            | {
                "field": col_name,
                "columnGroupShow": "open",
                "valueFormatter": {
                    "function": "params.value ? params.value.toExponential(2) : null;"  # noqa: E501
                },
            }
            for col_name in abundance_col_names
        ]


@dataclass(frozen=True)
class LipidData(GridData):
    @classmethod
    def from_serialized(
        cls,
        records: list[dict],
        full_col_names: list[str],
        name_col_name: str,
        vec_col_names: list[str],
        smiles_col_name: str,
        lipid_header: str,
        vecs_header: str,
    ) -> Self:
        return cls(
            records=records,
            col_groups_defs=cls._gen_col_group_defs(
                full_col_names,
                name_col_name,
                vec_col_names,
                smiles_col_name,
                lipid_header,
                vecs_header,
            ),
        )

    @classmethod
    def _gen_col_group_defs(
        cls,
        full_col_names: list[str],
        name_col_name: str,
        vec_col_names: list[str],
        smiles_col_name: str,
        lipid_header: str,
        vecs_header: str,
    ) -> list[dict]:
        features_col_defs: list[dict] = [
            cls._COMMON_COL_DEF_PARAMS
            | {
                "field": name_col_name,
            }
        ] + [
            cls._COMMON_COL_DEF_PARAMS | {"field": name}
            for name in full_col_names
            if name != smiles_col_name and name not in vec_col_names
        ]

        vec_col_defs: list[dict] = [
            cls._COMMON_COL_DEF_PARAMS
            | {
                "field": name,
                "filter": "agNumberColumnFilter",
                "columnGroupShow": (
                    "open" if name != vec_col_names[0] else None
                ),
                "valueFormatter": {
                    "function": "params.value ? params.value.toExponential(2) : null;"  # noqa: E501
                },
            }
            for name in vec_col_names
        ]

        col_group_defs: list[dict] = [
            {"headerName": lipid_header, "children": features_col_defs},
            {"headerName": vecs_header, "children": vec_col_defs},
        ]

        return col_group_defs


@dataclass(frozen=True)
class ChangeData(GridData):
    @classmethod
    def from_serialized(
        cls,
        records: list[dict],
        idx_names: list[str],
        col_names: list[str],
        change_header: str,
    ) -> Self:
        return cls(
            records=records,
            col_groups_defs=cls._gen_col_group_defs(
                idx_names, col_names, change_header
            ),
        )

    @classmethod
    def _gen_col_group_defs(
        cls,
        idx_names: list[str],
        col_names: list[str],
        change_header: str,
    ) -> list[dict]:
        idx_col_defs: list[dict] = [
            cls._COMMON_COL_DEF_PARAMS
            | {"field": name, "columnGroupShow": "open"}
            for name in idx_names
        ]

        val_col_defs: list[dict] = [
            cls._COMMON_COL_DEF_PARAMS
            | {
                "field": col,
                "filter": "agNumberColumnFilter",
                "columnGroupShow": "open",
                "valueFormatter": {
                    "function": "params.value ? params.value.toExponential(2) : null;"  # noqa: E501
                },
            }
            for col in col_names
        ]

        col_group_defs: list[dict] = [
            {
                "headerName": change_header,
                "children": idx_col_defs + val_col_defs,
            }
        ]

        return col_group_defs


@dataclass(frozen=True)
class GridDataCollection:
    lipidome_data: LipidomeData
    lipid_data: LipidData
    difference_data: ChangeData
    log2fc_data: ChangeData

    @classmethod
    def from_records(
        cls,
        lipidome_records: list[dict],
        lipidome_virtual_records: list[dict],
        lipidome_col_groups_defs: list[dict],
        lipidome_selected_rows: list[dict],
        lipid_records: list[dict],
        lipid_virtual_records: list[dict],
        lipid_col_groups_defs: list[dict],
        lipid_selected_rows: list[dict],
        difference_records: list[dict],
        difference_virtual_records: list[dict],
        difference_col_groups_defs: list[dict],
        difference_selected_rows: list[dict],
        log2fc_records: list[dict],
        log2fc_virtual_records: list[dict],
        log2fc_col_groups_defs: list[dict],
        log2fc_selected_rows: list[dict],
    ) -> Self:
        return cls(
            LipidomeData(
                lipidome_records,
                lipidome_virtual_records,
                lipidome_col_groups_defs,
                lipidome_selected_rows,
            ),
            LipidData(
                lipid_records,
                lipid_virtual_records,
                lipid_col_groups_defs,
                lipid_selected_rows,
            ),
            ChangeData(
                difference_records,
                difference_virtual_records,
                difference_col_groups_defs,
                difference_selected_rows,
            ),
            ChangeData(
                log2fc_records,
                log2fc_virtual_records,
                log2fc_col_groups_defs,
                log2fc_selected_rows,
            ),
        )

    @classmethod
    def from_dict(cls, input_dict: dict) -> Self:
        return cls(
            LipidomeData.from_dict(input_dict["lipidome_data"]),
            LipidData.from_dict(input_dict["lipid_data"]),
            ChangeData.from_dict(input_dict["difference_data"]),
            ChangeData.from_dict(input_dict["log2fc_data"]),
        )

    def gen_serialized_dict(self) -> dict:
        return {
            "lipidome_data": self.lipidome_data.serialize(),
            "lipid_data": self.lipid_data.serialize(),
            "difference_data": self.difference_data.serialize(),
            "log2fc_data": self.log2fc_data.serialize(),
        }
