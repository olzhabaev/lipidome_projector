"""Module concerning the processing of databases."""

import logging

from lipid_vector_space.databases.base_db_processor import BaseDBProcessor


logger: logging.Logger = logging.getLogger(__name__)


class Databases:
    def __init__(self, db_processors: list[BaseDBProcessor]) -> None:
        self._db_processors: list[BaseDBProcessor] = db_processors

    def proc_and_write_structures(self) -> None:
        for db in self._db_processors:
            db.proc_and_write_structures()

    def parse_and_write(self) -> None:
        for db in self._db_processors:
            db.parse_and_write()
