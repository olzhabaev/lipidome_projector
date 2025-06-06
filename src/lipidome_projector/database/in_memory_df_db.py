"""Module containing a simple in memory dataframe database class."""

import logging
import tomllib

from collections import defaultdict
from dataclasses import dataclass, field
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Self

import pandas as pd

from lipid_data_processing.notation.parsing import ParsedDataset

from lipidome_projector.database.base_db import BaseDB


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DBCfg:
    name: str
    db_path: Path
    vectors_2d_path: Path
    vectors_3d_path: Path
    smiles_path: Path

    @classmethod
    def from_cfg_file(cls, cfg_path: Path) -> Self:
        """Create a database configuration from a toml file.
        :param cfg_path: The path to the toml file.
        :returns: The database configuration.
        """
        with open(cfg_path, "rb") as config_file:
            cfg_dict: dict = tomllib.load(config_file)

        return cls(**cfg_dict)

    @classmethod
    def from_cfg_with_anchor(cls, cfg_dict: dict, anchor: Traversable) -> Self:
        """Create a database configuration from a dictionary.
        :param cfg_dict: The database configuration.
        :param anchor: The anchor for the paths.
        :returns: The database configuration.
        """
        return cls(
            name=cfg_dict["name"],
            db_path=Path(str(anchor.joinpath(cfg_dict["db_path"]))),
            vectors_2d_path=Path(
                str(anchor.joinpath(cfg_dict["vectors_2d_path"]))
            ),
            vectors_3d_path=Path(
                str(anchor.joinpath(cfg_dict["vectors_3d_path"]))
            ),
            smiles_path=Path(str(anchor.joinpath(cfg_dict["smiles_path"]))),
        )

    @classmethod
    def from_cfg_file_with_anchor(
        cls, cfg_path: Path, anchor: Traversable
    ) -> Self:
        """Create a database configuration from a toml file.
        :param cfg_path: The path to the toml file.
        :param anchor: The anchor for the paths.
        :returns: The database configuration.
        """
        with open(cfg_path, "rb") as config_file:
            cfg_dict: dict = tomllib.load(config_file)

        return cls.from_cfg_with_anchor(cfg_dict, anchor)


@dataclass(frozen=True)
class InMemoryDataFrameDB(BaseDB):
    name: str
    db_df: pd.DataFrame
    vectors_2d: pd.DataFrame
    vectors_3d: pd.DataFrame
    smiles: pd.Series

    vectors_combined: pd.DataFrame = field(init=False)
    matching_ds: ParsedDataset = field(init=False)

    @classmethod
    def from_cfg(cls, cfg: DBCfg) -> Self:
        """Create a database from a configuration.
        :param cfg: The database configuration.
        :returns: The database.
        """
        return cls.from_files(
            name=cfg.name,
            db_path=cfg.db_path,
            vectors_2d_path=cfg.vectors_2d_path,
            vectors_3d_path=cfg.vectors_3d_path,
            smiles_path=cfg.smiles_path,
        )

    @classmethod
    def from_files(
        cls,
        name: str,
        db_path: Path,
        vectors_2d_path: Path,
        vectors_3d_path: Path,
        smiles_path: Path,
    ) -> Self:
        """Read a database from the drive.
        :param name: The name of the database.
        :param db_path: The path to the parsed database.
        :param vectors_2d_path: The path to the 2D vectors.
        :param vectors_3d_path: The path to the 3D vectors.
        :param smiles_path: The path to the SMILES file.
        :returns: The database.
        """
        return cls(
            name=name,
            db_df=cls._read_db_file(db_path, str),
            vectors_2d=cls._read_db_file(vectors_2d_path, float),
            vectors_3d=cls._read_db_file(vectors_3d_path, float),
            smiles=cls._read_db_file(smiles_path, str).squeeze(),
        )

    def __post_init__(self) -> None:
        self._chk_indexes()
        self._set_combined_vectors()
        self._set_matching_ds()

    def _chk_indexes(self) -> None:
        db_vec2d_sym_diff: pd.Index = self.db_df.index.symmetric_difference(
            self.vectors_2d.index,
        )
        if not db_vec2d_sym_diff.empty:
            raise ValueError(
                f"Database and 2D vectors have differing indexes: "
                f"{db_vec2d_sym_diff}"
            )

        db_vec3d_sym_diff: pd.Index = self.db_df.index.symmetric_difference(
            self.vectors_3d.index,
        )
        if not db_vec3d_sym_diff.empty:
            raise ValueError(
                f"Database and 3D vectors have differing indexes: "
                f"{db_vec3d_sym_diff}"
            )

        db_smiles_sym_diff: pd.Index = self.db_df.index.symmetric_difference(
            self.smiles.index,
        )
        if not db_smiles_sym_diff.empty:
            raise ValueError(
                f"Database and SMILES have differing indexes: "
                f"{db_smiles_sym_diff}"
            )

    def _set_combined_vectors(self) -> None:
        vectors_combined: pd.DataFrame = pd.concat(
            [self.vectors_2d, self.vectors_3d],
            axis="columns",
            join="inner",
            verify_integrity=True,
        )

        object.__setattr__(self, "vectors_combined", vectors_combined)

    def _set_matching_ds(self) -> None:
        matching_ds: ParsedDataset = ParsedDataset(
            df=self.db_df.fillna("")
        ).get_component_complete_subset()

        object.__setattr__(self, "matching_ds", matching_ds)

    @staticmethod
    def _read_db_file(path: Path, dtype: type) -> pd.DataFrame:
        logger.info(f"Read database file: {path}")

        dtype_dict: defaultdict = defaultdict(lambda: dtype)
        dtype_dict[0] = str

        match filetype := path.suffix:
            case ".csv" | ".zip":
                df: pd.DataFrame = pd.read_csv(
                    path,
                    index_col=0,
                    dtype=dtype_dict,
                )
            case ".pkl":
                df: pd.DataFrame = pd.read_pickle(path)
            case _:
                raise ValueError(f"Unknown filetype {filetype}")

        return df
