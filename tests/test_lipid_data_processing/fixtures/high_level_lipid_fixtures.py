"""Module concerning high level lipid fixtures."""

import logging

import pandas as pd
import pytest

from tests.test_lipid_data_processing.util.lipid_description import (
    LipidCollection,
    LipidDescription,
    ParsedLipid,
)

logger: logging.Logger = logging.getLogger(__name__)


# * LIPID DEFINITIONS ---------------------------------------------------------

# ** GL -----------------------------------------------------------------------


@pytest.fixture(scope="session")
def dg_sp_24_0() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="DG(24:0)",
        parsed_name="DG 24:0",
        level="SPECIES",
        category="GL",
        class_="DG",
        species="DG 24:0",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="MISSING",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def dg_sp_24_2() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="DG(24:2)",
        parsed_name="DG 24:2",
        level="SPECIES",
        category="GL",
        class_="DG",
        species="DG 24:2",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="MISSING",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def dg_sp_26_1() -> LipidDescription:
    original_name: str = "DG(26:1)"

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 26:1",
        level="SPECIES",
        category="GL",
        class_="DG",
        species="DG 26:1",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="MISSING",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def dg_sp_32_0() -> LipidDescription:
    original_name: str = "DG(32:0)"

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 32:0",
        level="SPECIES",
        category="GL",
        class_="DG",
        species="DG 32:0",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="MISSING",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def dg_sp_32_1() -> LipidDescription:
    original_name: str = "DG(32:1)"

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 32:1",
        level="SPECIES",
        category="GL",
        class_="DG",
        species="DG 32:1",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="MISSING",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def tg_sp_54_3() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="TG(54:3)",
        parsed_name="TG 54:3",
        level="SPECIES",
        category="GL",
        class_="TG",
        species="TG 54:3",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="MISSING",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


# ** GP -----------------------------------------------------------------------


@pytest.fixture(scope="session")
def pc_sp_34_4() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="PC(34:4)",
        parsed_name="PC 34:4",
        level="SPECIES",
        category="GP",
        class_="PC",
        species="PC 34:4",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def pe_sp_34_3() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="PE(34:3)",
        parsed_name="PE 34:3",
        level="SPECIES",
        category="GP",
        class_="PE",
        species="PE 34:3",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="MISSING",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


# ** SP ----------------------------------------------------------------------


@pytest.fixture(scope="session")
def cer_sp_34_1_2() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="Cer(d34:1)",
        parsed_name="Cer 34:1;O2",
        level="SPECIES",
        category="SP",
        class_="Cer",
        species="Cer 34:1;O2",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="MISSING",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


@pytest.fixture(scope="session")
def hex_cer_38_4_2() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="HexCer(d38:4)",
        parsed_name="HexCer 38:4;O2",
        level="SPECIES",
        category="SP",
        class_="HexCer",
        species="HexCer 38:4;O2",
        molecular_species="UNDEFINED",
        sn_position="UNDEFINED",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="MISSING",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="MISSING",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


# ** ST ----------------------------------------------------------------------


@pytest.fixture(scope="session")
def teasterone() -> LipidDescription:
    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name="Teasterone",
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
        original_name=parsed_lipid.original_name,
        parsed_lipid=parsed_lipid,
    )

    return lipid_description


# * GROUP FIXTURES -----------------------------------------------------------


@pytest.fixture(scope="session")
def all_high_level_lipids(
    dg_sp_24_0: LipidDescription,
    dg_sp_24_2: LipidDescription,
    dg_sp_32_0: LipidDescription,
    dg_sp_32_1: LipidDescription,
    tg_sp_54_3: LipidDescription,
    pc_sp_34_4: LipidDescription,
    pe_sp_34_3: LipidDescription,
    cer_sp_34_1_2: LipidDescription,
    hex_cer_38_4_2: LipidDescription,
    teasterone: LipidDescription,
) -> LipidCollection:
    return LipidCollection(
        [
            dg_sp_24_0,
            dg_sp_24_2,
            dg_sp_32_0,
            dg_sp_32_1,
            tg_sp_54_3,
            pc_sp_34_4,
            pe_sp_34_3,
            cer_sp_34_1_2,
            hex_cer_38_4_2,
            teasterone,
        ]
    )


@pytest.fixture(scope="session")
def all_high_level_original_names(
    all_high_level_lipids: LipidCollection,
) -> pd.Series:
    return all_high_level_lipids.to_original_name_series()


@pytest.fixture(scope="session")
def all_high_level_parsed_df(
    all_high_level_lipids: LipidCollection,
) -> pd.DataFrame:
    return all_high_level_lipids.to_parsed_df()
