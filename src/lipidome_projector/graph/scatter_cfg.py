""" """

import logging

from dataclasses import dataclass
from typing import Literal, Self


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScatterCfg:
    mode: Literal["lipidome", "difference", "log2fc"]
    dim: Literal[2, 3]
    sizemode: Literal["area", "diameter"]
    scaling_method: Literal["linear", "min_max"]
    min_max_scaling_value: tuple[float, float]
    linear_scaling_factor: float
    linear_scaling_base: float
    template: str

    @classmethod
    def from_dict(cls, input_dict: dict) -> Self:
        return cls(**input_dict)
