"""Module concerning miscellaneous lipid fixtures."""

import logging

import pytest

from tests.test_lipid_data_processing.util.lipid_description import (
    LipidDescription,
    ParsedLipid,
)

logger: logging.Logger = logging.getLogger(__name__)


# * LIPID DEFINITIONS ---------------------------------------------------------

# ** UNPARSEABLE NAMES --------------------------------------------------------


@pytest.fixture(scope="session")
def unparseable_name_1() -> LipidDescription:
    original_name: str = "UNPARSEABLE_NAME_1"

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="",
        level="",
        category="",
        class_="",
        species="",
        molecular_species="",
        sn_position="",
        structure_defined="",
        full_structure="",
        complete_structure="",
        fa1="",
        fa2="",
        fa3="",
        fa4="",
        lcb="",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description
