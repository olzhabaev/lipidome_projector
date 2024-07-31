"""Module concerning the SwissLipids processor class."""

import logging

from lipid_data_processing.databases.base_db_classes import Database
from lipid_data_processing.databases.swiss_lipids import SwissLipids
from lipid_vector_space.databases.base_db_processor import BaseDBProcessor


logger: logging.Logger = logging.getLogger(__name__)


class SLProcessor(BaseDBProcessor):
    @property
    def db_name(self) -> str:
        return "sl"

    def _load_db(self) -> Database:
        return SwissLipids.from_source_file(
            self._source_file_path, drop_non_isomers=True, add_rdkit_data=False
        )
