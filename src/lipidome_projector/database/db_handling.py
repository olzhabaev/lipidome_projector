"""Module concerning the handling of databases."""

import logging
import tomllib

from pathlib import Path

from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.database.in_memory_df_db import InMemoryDataFrameDB


logger: logging.Logger = logging.getLogger(__name__)


def create_database(config_path: Path) -> BaseDB:
    """Create a database from a configuration.
    :param config_path: Path to the database configuration file.
    :returns: The database.
    :raises ValueError: If the database type is unknown.
    """
    logger.info("Create database.")

    db_config_dict: dict = _load_db_config_dict(config_path)

    if db_config_dict["type"] == "in_memory_db_df":
        database: InMemoryDataFrameDB = InMemoryDataFrameDB.from_config_dict(
            db_config_dict
        )
    else:
        raise ValueError(f"Unknown database type {type(db_config_dict)}")

    return database


def _load_db_config_dict(config_path: Path) -> dict:
    logger.info("Read database configuration.")

    with open(config_path, "rb") as config_file:
        config_dict: dict = tomllib.load(config_file)

    if "type" not in config_dict:
        raise ValueError("Database configuration must contain a type.")

    return config_dict
