"""Module concerning plotly scatter markers for lipids."""

import logging

import plotly.express as px


logger: logging.Logger = logging.getLogger(__name__)


_BASE_PALETTE: list[str] = px.colors.qualitative.T10


# TODO: Check whether these need updating.
CATEGORY_COLORS: dict[str, str] = {
    "Fatty Acyls [FA]": _BASE_PALETTE[0],
    "Glycerolipids [GL]": _BASE_PALETTE[1],
    "Glycerophospholipids [GP]": _BASE_PALETTE[4],
    "Sphingolipids [SP]": _BASE_PALETTE[2],
    "Sterol Lipids [ST]": _BASE_PALETTE[6],
    "Prenol Lipids [PR]": _BASE_PALETTE[8],
    "Saccharolipids [SL]": _BASE_PALETTE[3],
    "Polyketides [PK]": _BASE_PALETTE[9],
    "FA": _BASE_PALETTE[0],
    "GL": _BASE_PALETTE[1],
    "GP": _BASE_PALETTE[4],
    "SP": _BASE_PALETTE[2],
    "ST": _BASE_PALETTE[6],
    "PR": _BASE_PALETTE[8],
    "SL": _BASE_PALETTE[3],
    "PK": _BASE_PALETTE[9],
    "UNDEFINED": _BASE_PALETTE[9],
    "OTHER": _BASE_PALETTE[9],
}


CATEGORY_SYMBOLS_2D: dict[str, int] = {
    "Fatty Acyls [FA]": 0,
    "Glycerolipids [GL]": 1,
    "Glycerophospholipids [GP]": 1,
    "Sphingolipids [SP]": 4,
    "Sterol Lipids [ST]": 2,
    "Prenol Lipids [PR]": 2,
    "Saccharolipids [SL]": 3,
    "Polyketides [PK]": 0,
    "FA": 0,
    "GL": 1,
    "GP": 1,
    "SP": 4,
    "ST": 2,
    "PR": 2,
    "SL": 3,
    "PK": 0,
    "UNDEFINED": 0,
    "OTHER": 0,
}


CATEGORY_SYMBOLS_3D: dict[str, str] = {
    "Fatty Acyls [FA]": "circle",
    "Glycerolipids [GL]": "square",
    "Glycerophospholipids [GP]": "square",
    "Sphingolipids [SP]": "x",
    "Sterol Lipids [ST]": "diamond",
    "Prenol Lipids [PR]": "diamond",
    "Saccharolipids [SL]": "cross",
    "Polyketides [PK]": "circle",
    "FA": "circle",
    "GL": "square",
    "GP": "square",
    "SP": "x",
    "ST": "diamond",
    "PR": "diamond",
    "SL": "cross",
    "PK": "circle",
    "UNDEFINED": "circle",
    "OTHER": "circle",
}
