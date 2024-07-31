"""Module concerning the LMSD processor class."""

import logging

from lipid_data_processing.databases.base_db_classes import Database
from lipid_data_processing.databases.lmsd import LMSD
from lipid_vector_space.databases.base_db_processor import BaseDBProcessor


logger: logging.Logger = logging.getLogger(__name__)


class LMSDProcessor(BaseDBProcessor):
    @property
    def db_name(self) -> str:
        return "lmsd"

    def _load_db(self) -> Database:
        return LMSD.from_source_file(
            self._source_file_path, add_rdkit_data=True
        )
