"""Module concerning lipidome grid data."""

import logging

from dataclasses import dataclass, field, fields


logger: logging.Logger = logging.getLogger(__name__)

# TODO: Decompose and extend abstraction.
# TODO: Introduce base and specific grid abstractions.


@dataclass(frozen=True)
class LipidomeFrontEndData:
    name: str = ""

    lipidome_records: list[dict] = field(default_factory=list)
    lipidome_virtual_records: list[dict] = field(default_factory=list)
    lipidome_col_groups_defs: list[dict] = field(default_factory=list)
    lipidome_selected_records: list[dict] = field(default_factory=list)

    lipid_records: list[dict] = field(default_factory=list)
    lipid_virtual_records: list[dict] = field(default_factory=list)
    lipid_col_groups_defs: list[dict] = field(default_factory=list)

    difference_records: list[dict] = field(default_factory=list)
    difference_virtual_records: list[dict] = field(default_factory=list)
    difference_col_groups_defs: list[dict] = field(default_factory=list)
    difference_selected_rows: list[dict] = field(default_factory=list)

    log2fc_records: list[dict] = field(default_factory=list)
    log2fc_virtual_records: list[dict] = field(default_factory=list)
    log2fc_col_groups_defs: list[dict] = field(default_factory=list)
    log2fc_selected_rows: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._set_list_if_none()

    def _set_list_if_none(self) -> None:
        for field_ in fields(self):
            if getattr(self, field_.name) is None:
                object.__setattr__(self, field_.name, list())

    def grids_complete(self) -> bool:
        """Check if the grid is complete, i.e. whether all records
        are present.
        :returns: True if the grid is complete, False otherwise.
        """
        if len(self.lipidome_records) == 0 or len(self.lipid_records) == 0:
            return False

        if len(self.lipidome_virtual_records) == 0:
            return False

        if len(self.lipid_virtual_records) == 0:
            return False

        return True
