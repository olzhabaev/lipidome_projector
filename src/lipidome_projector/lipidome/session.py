""" """

import logging
import json

from dataclasses import asdict, dataclass
from typing import Self

from lipidome_projector.graph.scatter_cfg import ScatterCfg
from lipidome_projector.lipidome.grid_data import GridDataCollection

logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SessionState:
    gdc: GridDataCollection
    scatter_cfg: ScatterCfg
    lipidome_filter_model: dict
    lipid_filter_model: dict
    difference_filter_model: dict
    log2fc_filter_model: dict

    @classmethod
    def from_dict(cls, input_dict: dict) -> Self:
        grid_data: GridDataCollection = GridDataCollection.from_dict(
            input_dict["gdc"]
        )
        scatter_cfg: ScatterCfg = ScatterCfg.from_dict(
            input_dict["scatter_cfg"]
        )

        return cls(
            grid_data,
            scatter_cfg,
            input_dict["lipidome_filter_model"],
            input_dict["lipid_filter_model"],
            input_dict["difference_filter_model"],
            input_dict["log2fc_filter_model"],
        )

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        content_dict: dict = json.loads(json_str)
        return cls.from_dict(content_dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
