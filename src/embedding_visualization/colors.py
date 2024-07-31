"""Module concerning colors."""

import colorsys
import logging

from itertools import cycle
from typing import cast, Literal

import plotly.express as px


logger: logging.Logger = logging.getLogger(__name__)


CONTINUOUS_COLORSCALES: dict[str, list[str]] = {
    "bluered": px.colors.sequential.RdBu_r,
    "redblue": px.colors.sequential.RdBu,
    "blue_asc": px.colors.sequential.Blues,
    "blue_desc": px.colors.sequential.Blues_r,
    "red_asc": px.colors.sequential.Reds,
    "red_desc": px.colors.sequential.Reds_r,
    "thermal": px.colors.sequential.thermal,
}


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a hex string.
    :param rgb: The RGB tuple to convert.
    :return: The hex string.
    """
    hex_color: str = "#{:02x}{:02x}{:02x}".format(*rgb)

    return hex_color


def rgb_str_to_hex(rgb: str) -> str:
    """Convert an RGB string to a hex string.
    :param rgb: The RGB string of format 'rgb(r, g, b)'.
    :return: The hex string.
    """
    return "#{:02x}{:02x}{:02x}".format(
        *(int(val) for val in rgb[4:-1].split(","))
    )


def rgb_str_list_to_hex(rgb_list: list[str]) -> list[str]:
    """Convert a list of RGB strings to a list of hex strings.
    :param rgb_list: The list of RGB strings.
    :return: The list of hex strings.
    """
    return [rgb_str_to_hex(rgb) for rgb in rgb_list]


def is_valid_hex_string(hex_color: str) -> bool:
    """Check if a hex color string is valid.
    :param hex_color: The hex color string to check (must include '#').
    :return: True if valid, False otherwise.
    """
    return (
        len(hex_color) == 7
        and all(
            0 <= int(hex_color[i : i + 2], 16) <= 255  # noqa E203
            for i in (1, 3, 5)
        )
        and hex_color[0] == "#"
    )


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex string to an RGB tuple.
    :param hex_color: The hex string to convert (must include '#').
    :return: The RGB tuple.
    """
    if not is_valid_hex_string(hex_color):
        raise ValueError(f"Invalid hex color {hex_color}.")

    return cast(
        tuple[int, int, int],
        tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5)),  # noqa E203
    )


def generate_discrete_hex_colormap(
    classes: list[str], style: Literal["T10"]
) -> dict[str, str]:
    """Generate a colormap for discrete class names.
    :param classes: The class names to generate a colormap for.
    :param style: The style of the colormap. One of ["T10"].
    :return: A colormap dict for the classes.
    :raises ValueError: If the style is unknown.
    """
    if style == "T10":
        palette: cycle[str] = cycle(px.colors.qualitative.T10)
    else:
        raise ValueError(f"Unknown style {style}.")

    colormap: dict[str, str] = dict(zip(classes, palette))

    return colormap


def darken_hex_color(hex_color: str) -> str:
    """Darken a hex color.
    :param hex_color: The hex color string to darken (must include '#').
    :return: The darkened hex color string (includes '#').
    """
    if not is_valid_hex_string(hex_color):
        raise ValueError(f"Invalid hex color {hex_color}.")

    rgb: tuple[int, int, int] = hex_to_rgb(hex_color)

    hls: tuple[float, float, float] = colorsys.rgb_to_hls(
        rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    )

    h: float = hls[0]
    l: float = hls[1]
    s: float = hls[2]

    ln: float = max(0, l * 0.7)
    sn: float = min(1, s * 1.4)

    rgbn: tuple[float, float, float] = colorsys.hls_to_rgb(h, ln, sn)

    rn: int = int(rgbn[0] * 255)
    gn: int = int(rgbn[1] * 255)
    bn: int = int(rgbn[2] * 255)

    darker_hex_color: str = f"#{rn:02x}{gn:02x}{bn:02x}"

    return darker_hex_color


def average_hex_color(hex_colors: list[str]) -> str:
    """Average a list of hex colors.
    :param hex_colors: The hex colors to average (must include '#').
    :return: The averaged hex color string (includes '#').
    """
    rgb_colors: list[tuple[int, int, int]] = [
        hex_to_rgb(hex) for hex in hex_colors
    ]

    avg_rgb: tuple[int, int, int] = (
        int(sum(color[0] for color in rgb_colors) / len(rgb_colors)),
        int(sum(color[1] for color in rgb_colors) / len(rgb_colors)),
        int(sum(color[2] for color in rgb_colors) / len(rgb_colors)),
    )

    avg_hex: str = "#{:02x}{:02x}{:02x}".format(*avg_rgb)

    return avg_hex
