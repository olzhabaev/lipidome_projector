"""Module concerning symbols."""

import logging

from typing import Literal


logger: logging.Logger = logging.getLogger(__name__)


SYMBOLS_2D: list[int] = [
    0,  # circle
    100,  # circle-open
    3,  # cross
    2,  # diamond
    102,  # diamond-open
    1,  # square
    101,  # square-open
    4,  # x
]


SYMBOLS_3D: list[str] = [
    "circle",
    "circle-open",
    "cross",
    "diamond",
    "diamond-open",
    "square",
    "square-open",
    "x",
]


def gen_symbol_map(
    classes: list[str], dimensionality: Literal[2, 3]
) -> dict[str, int] | dict[str, str]:
    """Generate symbol map.
    :param classes: Classes.
    :param dimensionality: Dimensionality.
    :return: Symbol map.
    """
    symbols: list = SYMBOLS_2D if dimensionality == 2 else SYMBOLS_3D
    return {cls: symbols[i % len(symbols)] for i, cls in enumerate(classes)}
