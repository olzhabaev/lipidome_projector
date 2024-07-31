"""Module concerning graph settings."""

import logging

from dataclasses import dataclass


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GraphSettings:
    mode: str
    dimensionality: int
    sizemode: str
    scaling_method: str
    min_max_scaling_value: tuple[float, float]
    linear_scaling_factor: float
    linear_scaling_base: float
    template: str
