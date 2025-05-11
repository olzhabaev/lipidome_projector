"""Module concerning the processing of default datasets."""

import logging
import tomllib

from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Self

from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset
from lipid_data_processing.notation.matching import ConstraintsDataset

from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.lipidome_ds_postprocessing import (
    process_lipidome_ds,
)
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.lipidome.translation import (
    lipidome_ds_to_lipidome_fe_data,
)
from lipidome_projector.lipidome.upload_processing import (
    match,
)


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DefaultDatasetCfg:
    name: str
    abundances_csv_path: Path
    lipidome_features_csv_path: Path
    fa_constraints_csv_path: Path
    lcb_constraints_csv_path: Path
    description: str

    @classmethod
    def from_dict_with_anchor(
        cls, cfg_dict: dict, anchor: Traversable
    ) -> Self:
        """Create a dataset configuration from a dictionary.
        :param cfg_dict: The dataset configuration.
        :param anchor: The anchor for the paths.
        :returns: The dataset configuration.
        """
        return cls(
            name=cfg_dict["name"],
            abundances_csv_path=Path(
                str(anchor.joinpath(cfg_dict["abundances_csv_path"]))
            ),
            lipidome_features_csv_path=Path(
                str(anchor.joinpath(cfg_dict["lipidome_features_csv_path"]))
            ),
            fa_constraints_csv_path=Path(
                str(anchor.joinpath(cfg_dict["fa_constraints_csv_path"]))
            ),
            lcb_constraints_csv_path=Path(
                str(anchor.joinpath(cfg_dict["lcb_constraints_csv_path"]))
            ),
            description=cfg_dict["description"],
        )


class DefaultLipidomeData:
    def __init__(
        self,
        datasets: dict[str, LipidomeDataset],
        dataset_descriptions: dict[str, str],
        col_names: ColNames,
    ) -> None:
        self._datasets: dict[str, LipidomeDataset] = datasets
        self._dataset_descriptions: dict[str, str] = dataset_descriptions
        self._col_names: ColNames = col_names

    @classmethod
    def from_cfgs(
        cls,
        dataset_cfgs: list[DefaultDatasetCfg],
        database: BaseDB,
        col_names: ColNames,
    ) -> Self:
        datasets: dict[str, LipidomeDataset] = {
            default_dataset_config.name: cls._gen_lipidome_ds(
                default_dataset_config, database, col_names
            )
            for default_dataset_config in dataset_cfgs
        }

        dataset_descriptions: dict[str, str] = {
            default_dataset_config.name: default_dataset_config.description
            for default_dataset_config in dataset_cfgs
        }

        return cls(datasets, dataset_descriptions, col_names)

    @classmethod
    def from_cfg_file(
        cls, path: Path, database: BaseDB, col_names: ColNames
    ) -> Self:
        logger.info(f"Load default lipidome data config file: '{path}'.")

        with open(path, "rb") as file:
            config_dict: dict = tomllib.load(file)

        dataset_cfgs: list[DefaultDatasetCfg] = [
            DefaultDatasetCfg(**dataset_config_dict)
            for dataset_config_dict in config_dict["datasets"]
        ]

        return cls.from_cfgs(dataset_cfgs, database, col_names)

    @classmethod
    def from_cfg_file_with_anchor(
        cls,
        path: Path,
        anchor: Traversable,
        database: BaseDB,
        col_names: ColNames,
    ) -> Self:
        logger.info(f"Load default lipidome data config file: '{path}'.")

        with open(path, "rb") as file:
            config_dict: dict = tomllib.load(file)

        dataset_cfgs: list[DefaultDatasetCfg] = [
            DefaultDatasetCfg.from_dict_with_anchor(
                dataset_config_dict, anchor
            )
            for dataset_config_dict in config_dict["datasets"]
        ]

        return cls.from_cfgs(dataset_cfgs, database, col_names)

    # TODO: Extract, this is not the concern of this class.
    def load_default_dataset(self, name: str) -> LipidomeFrontEndData:
        lipidome_ds: LipidomeDataset = self._datasets[name]

        lipidome_fe_data: LipidomeFrontEndData = (
            lipidome_ds_to_lipidome_fe_data(lipidome_ds, self._col_names)
        )

        return lipidome_fe_data

    @classmethod
    def _gen_lipidome_ds(
        cls,
        dataset_cfg: DefaultDatasetCfg,
        database: BaseDB,
        col_names: ColNames,
    ) -> LipidomeDataset:
        logger.info(
            f"Load default and match lipidome dataset '{dataset_cfg.name}'."
        )

        initial_lipidome_ds: LipidomeDataset = LipidomeDataset.from_csv_input(
            dataset_cfg.name,
            dataset_cfg.abundances_csv_path,
            dataset_cfg.lipidome_features_csv_path,
        )

        constraints_ds: ConstraintsDataset = (
            ConstraintsDataset.from_constraint_csv_input(
                dataset_cfg.fa_constraints_csv_path,
                dataset_cfg.lcb_constraints_csv_path,
            )
        )

        lipidome_ds: LipidomeDataset
        lipidome_ds, _ = match(
            initial_lipidome_ds, constraints_ds, database, col_names.lipid
        )

        process_lipidome_ds(lipidome_ds, col_names)

        return lipidome_ds
