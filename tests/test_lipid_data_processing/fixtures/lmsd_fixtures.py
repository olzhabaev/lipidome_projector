"""Module concerning SwissLipids fixtures."""

import logging

from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from _pytest.tmpdir import TempPathFactory

from lipid_data_processing.databases.lmsd import LMSD

from tests.test_lipid_data_processing.util.lipid_description import (
    LipidCollection,
    LipidDescription,
    LMSDLipid,
    ParsedLipid,
)

logger: logging.Logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def lmsd_tmp_file_path(tmp_path_factory: TempPathFactory) -> Path:
    lmsd_tmp_file_path: Path = tmp_path_factory.mktemp("lmsd").joinpath(
        "lmsd.sdf"
    )

    with open(lmsd_tmp_file_path, "w") as file:
        file.write(_LMSD_SDF_STR)

    return lmsd_tmp_file_path


@pytest.fixture(scope="session")
def lmsd_lipids(
    lmgl02010009: LipidDescription,
    lmgl02010010: LipidDescription,
    lmgl03010233: LipidDescription,
    lmgl03010237: LipidDescription,
    lmsp02010004: LipidDescription,
    lmsp02010036: LipidDescription,
    lmst01010001: LipidDescription,
    lmst01010066: LipidDescription,
    lmst01030121: LipidDescription,
) -> LipidCollection:
    return LipidCollection(
        [
            lmgl02010009,
            lmgl02010010,
            lmgl03010233,
            lmgl03010237,
            lmsp02010004,
            lmsp02010036,
            lmst01010001,
            lmst01010066,
            lmst01030121,
        ]
    )


@pytest.fixture(scope="session")
def lmsd_df(lmsd_lipids: LipidCollection) -> pd.DataFrame:
    return lmsd_lipids.to_lmsd_df()


@pytest.fixture(scope="session")
def lmsd(lmsd_df: pd.DataFrame) -> LMSD:
    return LMSD(lmsd_df)


@pytest.fixture(scope="session")
def lmsd_generic_parsed_df(lmsd_lipids: LipidCollection) -> pd.DataFrame:
    return lmsd_lipids.to_lmsd_generic_parsed_df()


@pytest.fixture(scope="session")
def lmsd_sp_parsed_df(lmsd_lipids: LipidCollection) -> pd.DataFrame:
    return lmsd_lipids.to_lmsd_sp_parsed_df()


@pytest.fixture(scope="session")
def lmgl02010009() -> LipidDescription:
    original_name: str = "DG(16:0/16:0/0:0)"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMGL02010009",
        name=original_name,
        abbreviation="DG 32:0",
        category="Glycerolipids [GL]",
        class_="Diradylglycerols [GL02]",
        mass=568.506675,
        smiles="OC[C@]([H])(OC(CCCCCCCCCCCCCCC)=O)COC(CCCCCCCCCCCCCCC)=O",
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 16:0/16:0/0:0",
        level="FULL_STRUCTURE",
        category="GL",
        class_="DG",
        species="DG 32:0",
        molecular_species="DG 16:0_16:0",
        sn_position="DG 16:0/16:0/0:0",
        structure_defined="DG 16:0/16:0/0:0",
        full_structure="DG 16:0/16:0/0:0",
        complete_structure="UNDEFINED",
        fa1="16:0",
        fa2="16:0",
        fa3="0:0",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmgl02010010() -> LipidDescription:
    original_name: str = "DG(16:0/16:1(9Z)/0:0)[iso2]"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMGL02010010",
        name=original_name,
        abbreviation="DG 32:1",
        category="Glycerolipids [GL]",
        class_="Diradylglycerols [GL02]",
        mass=566.491025,
        smiles=r"OC[C@]([H])(OC(CCCCCCC/C=C\CCCCCC)=O)COC(CCCCCCCCCCCCCCC)=O",
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 16:0/16:1(9Z)/0:0",
        level="FULL_STRUCTURE",
        category="GL",
        class_="DG",
        species="DG 32:1",
        molecular_species="DG 16:0_16:1",
        sn_position="DG 16:0/16:1/0:0",
        structure_defined="DG 16:0/16:1(9)/0:0",
        full_structure="DG 16:0/16:1(9Z)/0:0",
        complete_structure="UNDEFINED",
        fa1="16:0",
        fa2="16:1(9Z)",
        fa3="0:0",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmgl03010233() -> LipidDescription:
    original_name: str = "TG(17:1(9Z)/17:2(9Z,12Z)/20:0)[iso6]"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMGL03010233",
        name=original_name,
        abbreviation="TG 54:3",
        category="Glycerolipids [GL]",
        class_="Triradylglycerols [GL03]",
        mass=884.783290,
        smiles=(
            r"C(OC(=O)CCCCCCCCCCCCCCCCCCC)[C@]([H])"
            r"(OC(CCCCCCC/C=C\C/C=C\CCCC)=O)COC(CCCCCCC/C=C\CCCCCCC)=O"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="TG 17:1(9Z)/17:2(9Z,12Z)/20:0",
        level="FULL_STRUCTURE",
        category="GL",
        class_="TG",
        species="TG 54:3",
        molecular_species="TG 17:1_17:2_20:0",
        sn_position="TG 17:1/17:2/20:0",
        structure_defined="TG 17:1(9)/17:2(9,12)/20:0",
        full_structure="TG 17:1(9Z)/17:2(9Z,12Z)/20:0",
        complete_structure="UNDEFINED",
        fa1="17:1(9Z)",
        fa2="17:2(9Z,12Z)",
        fa3="20:0",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmgl03010237() -> LipidDescription:
    original_name: str = "TG(17:1(9Z)/17:1(9Z)/20:1(11Z))[iso3]"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMGL03010237",
        name=original_name,
        abbreviation="TG 54:3",
        category="Glycerolipids [GL]",
        class_="Triradylglycerols [GL03]",
        mass=884.783290,
        smiles=(
            r"C(OC(=O)CCCCCCCCC/C=C\CCCCCCCC)"
            r"[C@]([H])(OC(CCCCCCC/C=C\CCCCCCC)=O)COC(CCCCCCC/C=C\CCCCCCC)=O"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="TG 17:1(9Z)/17:1(9Z)/20:1(11Z)",
        level="FULL_STRUCTURE",
        category="GL",
        class_="TG",
        species="TG 54:3",
        molecular_species="TG 17:1_17:1_20:1",
        sn_position="TG 17:1/17:1/20:1",
        structure_defined="TG 17:1(9)/17:1(9)/20:1(11)",
        full_structure="TG 17:1(9Z)/17:1(9Z)/20:1(11Z)",
        complete_structure="UNDEFINED",
        fa1="17:1(9Z)",
        fa2="17:1(9Z)",
        fa3="20:1(11Z)",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmsp02010004() -> LipidDescription:
    original_name: str = "Cer(d18:1/16:0)"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMSP02010004",
        name=original_name,
        abbreviation="Cer 34:1;O2",
        category="Sphingolipids [SP]",
        class_="Ceramides [SP02]",
        mass=537.512094,
        smiles=(
            r"[C@](CO)([H])(NC(CCCCCCCCCCCCCCC)=O)"
            "[C@]([H])(O)/C=C/CCCCCCCCCCCCC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="Cer 18:1;O2/16:0",
        level="SN_POSITION",
        category="SP",
        class_="Cer",
        species="Cer 34:1;O2",
        molecular_species="Cer 18:1;O2/16:0",
        sn_position="Cer 18:1;O2/16:0",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="16:0",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="18:1;1OH,3OH",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmsp02010036() -> LipidDescription:
    original_name: str = "Cer(d14:1/20:0)"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMSP02010036",
        name=original_name,
        abbreviation="Cer 34:1;O2",
        category="Sphingolipids [SP]",
        class_="Ceramides [SP02]",
        mass=537.512094,
        smiles=(
            r"[C@](CO)([H])(NC(CCCCCCCCCCCCCCCCCCC)=O)"
            "[C@]([H])(O)/C=C/CCCCCCCCC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="Cer 14:1;O2/20:0",
        level="SN_POSITION",
        category="SP",
        class_="Cer",
        species="Cer 34:1;O2",
        molecular_species="Cer 14:1;O2/20:0",
        sn_position="Cer 14:1;O2/20:0",
        structure_defined="UNDEFINED",
        full_structure="UNDEFINED",
        complete_structure="UNDEFINED",
        fa1="20:0",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="14:1;1OH,3OH",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmst01010001() -> LipidDescription:

    original_name: str = "Cholesterol"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMST01010001",
        name=original_name,
        abbreviation="ST 27:1;O",
        category="Sterol Lipids [ST]",
        class_="Sterols [ST01]",
        mass=386.354865,
        smiles=(
            r"[C@]12(CC=C3C[C@@H](O)CC[C@]3(C)[C@@]1([H])CC[C@]1(C)"
            r"[C@@]([H])([C@@](C)([H])CCCC(C)C)CC[C@@]21[H])[H]"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="ST 27:1;O",
        level="FULL_STRUCTURE",
        category="ST",
        class_="ST 27:1;O",
        species="ST 27:1;O",
        molecular_species="ST 27:1;O",
        sn_position="ST 27:1;O",
        structure_defined="ST 27:1;O",
        full_structure="ST 27:1;O",
        complete_structure="UNDEFINED",
        fa1="N/A",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmst01010066() -> LipidDescription:
    original_name: str = "Zymosterol"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMST01010066",
        name=original_name,
        abbreviation="ST 27:2;O",
        category="Sterol Lipids [ST]",
        class_="Sterols [ST01]",
        mass=384.339215,
        smiles=(
            r"C1[C@]2(C)C3CC[C@]4(C)[C@@]([H])([C@]([H])"
            r"(C)CC/C=C(\C)/C)CC[C@@]4([H])C=3CC[C@@]2([H])C[C@@H](O)C1"
        ),
    )

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

    lmsd_sp_parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="ST 27:2;O",
        level="COMPLETE_STRUCTURE",
        category="ST",
        class_="ST 27:2;O",
        species="ST 27:2;O",
        molecular_species="ST 27:2;O",
        sn_position="ST 27:2;O",
        structure_defined="ST 27:2;O",
        full_structure="ST 27:2;O",
        complete_structure="ST 27:2;O",
        fa1="N/A",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        lmsd_sp_parsed_lipid=lmsd_sp_parsed_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def lmst01030121() -> LipidDescription:
    original_name: str = "Teasterone"

    lmsd_lipid: LMSDLipid = LMSDLipid(
        index="LMST01030121",
        name=original_name,
        abbreviation="ST 28:1;O4",
        category="Sterol Lipids [ST]",
        class_="Sterols [ST01]",
        mass=448.355260,
        smiles=(
            r"[C@]12(CC(=O)[C@@]3([H])C[C@@H](O)CC[C@]3(C)"
            "[C@@]1([H])CC[C@]1(C)[C@@]([H])([C@@](C)([H])"
            "[C@@H](O)[C@H](O)[C@@H](C)C(C)C)CC[C@@]21[H])[H]"
        ),
    )

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

    lmsd_sp_parsed_lipid: ParsedLipid = replace(parsed_lipid, category="ST")

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        lmsd_lipid=lmsd_lipid,
        lmsd_sp_parsed_lipid=lmsd_sp_parsed_lipid,
        index=lmsd_lipid.index,
    )

    return lipid_description


# * DB SOURCE FILE STRING -----------------------------------------------------


_LMSD_SDF_STR: str = r"""LMGL02010009
  LIPID_MAPS_STRUCTURE_DATABASE

 41 40  0  0  0  0  0  0  0  0999 V2000
   19.3118    7.1933    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   18.6002    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.8883    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.1767    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.4650    7.1933    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   15.7533    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.7533    8.4256    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   18.2996    6.4815    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   17.4770    6.4815    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.7653    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.7653    5.2475    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.0537    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.0416    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.3368    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.6195    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.9023    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.1849    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.4677    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.7504    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.0332    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.3158    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.5985    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.8813    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.1640    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.4467    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7294    6.0703    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.0122    6.4815    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.3246    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.6074    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.8901    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.1728    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.4555    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7383    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0210    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.3036    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.5864    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.8691    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.1519    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.4345    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.7173    7.6030    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    7.1933    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  3  9  1  6  0  0  0
  3  8  1  0  0  0  0
  4  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  7  2  0  0  0  0
  6 13  1  0  0  0  0
  9 10  1  0  0  0  0
 10 11  2  0  0  0  0
 10 12  1  0  0  0  0
 12 14  1  0  0  0  0
 14 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 18  1  0  0  0  0
 18 19  1  0  0  0  0
 19 20  1  0  0  0  0
 20 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  1  0  0  0  0
 24 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  1  0  0  0  0
 13 28  1  0  0  0  0
 28 29  1  0  0  0  0
 29 30  1  0  0  0  0
 30 31  1  0  0  0  0
 31 32  1  0  0  0  0
 32 33  1  0  0  0  0
 33 34  1  0  0  0  0
 34 35  1  0  0  0  0
 35 36  1  0  0  0  0
 36 37  1  0  0  0  0
 37 38  1  0  0  0  0
 38 39  1  0  0  0  0
 39 40  1  0  0  0  0
 40 41  1  0  0  0  0
M  END

> <LM_ID>
LMGL02010009

> <NAME>
DG(16:0/16:0/0:0)

> <SYSTEMATIC_NAME>
1,2-dihexadecanoyl-sn-glycerol

> <CATEGORY>
Glycerolipids [GL]

> <MAIN_CLASS>
Diradylglycerols [GL02]

> <SUB_CLASS>
Diacylglycerols [GL0201]

> <EXACT_MASS>
568.506675

> <FORMULA>
C35H68O5

> <INCHI_KEY>
JEJLGIQLPYYGEE-XIFFEERXSA-N

> <INCHI>
InChI=1S/C35H68O5/c1-3-5-7-9-11-13-15-17-19-21-23-25-27-29-34(37)39-32-33(31-36)40-35(38)30-28-26-24-22-20-18-16-14-12-10-8-6-4-2/h33,36H,3-32H2,1-2H3/t33-/m0/s1

> <SMILES>
OC[C@]([H])(OC(CCCCCCCCCCCCCCC)=O)COC(CCCCCCCCCCCCCCC)=O

> <ABBREVIATION>
DG 32:0

> <SYNONYMS>
DG(16:0/16:0/0:0); DG(32:0); DG(16:0_16:0)

> <PUBCHEM_CID>
644078

> <HMDB_ID>
HMDB0007098

> <CHEBI_ID>
82929

> <SWISSLIPIDS_ID>
SLM:000118523

$$$$
LMGL02010010
  LIPID_MAPS_STRUCTURE_DATABASE

 41 40  0  0  0  0  0  0  0  0999 V2000
   19.3593    7.1998    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   18.6454    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.9311    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.2171    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.5030    7.1998    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   15.7890    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.7890    8.4362    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   18.3438    6.4856    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   17.5184    6.4856    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.8044    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.8044    5.2475    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.0905    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.0749    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.3711    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.6514    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.9318    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.2121    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.4925    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.7728    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.0531    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.3335    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.6138    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.8942    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.1745    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.4548    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7352    6.4856    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.0155    6.0730    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.3556    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.6359    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.9163    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.1966    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.4769    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7573    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0376    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.3180    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.5983    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.8786    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.1590    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.4393    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.7197    7.6109    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    7.1998    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  3  9  1  6  0  0  0
  3  8  1  1  0  0  0
  4  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  7  2  0  0  0  0
  6 13  1  0  0  0  0
  9 10  1  0  0  0  0
 10 11  2  0  0  0  0
 10 12  1  0  0  0  0
 12 14  1  0  0  0  0
 14 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 18  1  0  0  0  0
 18 19  1  0  0  0  0
 19 20  1  0  0  0  0
 20 21  2  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  1  0  0  0  0
 24 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  1  0  0  0  0
 13 28  1  0  0  0  0
 28 29  1  0  0  0  0
 29 30  1  0  0  0  0
 30 31  1  0  0  0  0
 31 32  1  0  0  0  0
 32 33  1  0  0  0  0
 33 34  1  0  0  0  0
 34 35  1  0  0  0  0
 35 36  1  0  0  0  0
 36 37  1  0  0  0  0
 37 38  1  0  0  0  0
 38 39  1  0  0  0  0
 39 40  1  0  0  0  0
 40 41  1  0  0  0  0
M  END

> <LM_ID>
LMGL02010010

> <NAME>
DG(16:0/16:1(9Z)/0:0)[iso2]

> <SYSTEMATIC_NAME>
1-hexadecanoyl-2-(9Z-hexadecenoyl)-sn-glycerol

> <CATEGORY>
Glycerolipids [GL]

> <MAIN_CLASS>
Diradylglycerols [GL02]

> <SUB_CLASS>
Diacylglycerols [GL0201]

> <EXACT_MASS>
566.491025

> <FORMULA>
C35H66O5

> <INCHI_KEY>
ADLOEVQMJKYKSR-YAIMUBSCSA-N

> <INCHI>
InChI=1S/C35H66O5/c1-3-5-7-9-11-13-15-17-19-21-23-25-27-29-34(37)39-32-33(31-36)40-35(38)30-28-26-24-22-20-18-16-14-12-10-8-6-4-2/h14,16,33,36H,3-13,15,17-32H2,1-2H3/b16-14-/t33-/m0/s1

> <SMILES>
OC[C@]([H])(OC(CCCCCCC/C=C\CCCCCC)=O)COC(CCCCCCCCCCCCCCC)=O

> <ABBREVIATION>
DG 32:1

> <SYNONYMS>
DG(16:0/16:1/0:0)[iso2]; DG(32:1); DG(16:0_16:1)

> <PUBCHEM_CID>
9543678

> <HMDB_ID>
HMDB0007099

> <CHEBI_ID>
84394

> <SWISSLIPIDS_ID>
SLM:000118430

$$$$
LMGL03010233
  LIPID_MAPS_STRUCTURE_DATABASE

 64 63  0  0  0  0  0  0  0  0999 V2000
   19.4017    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   18.6856    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.9698    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.2538    6.9572    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.5380    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.5380    8.1969    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   19.0993    6.2413    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   18.2718    6.2413    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   17.5560    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.5560    5.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.8402    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.8221    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   19.4017    8.1962    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   19.9862    8.7808    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   19.9862    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   20.7021    8.3673    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.1188    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.3973    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.6759    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.9544    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.2329    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.5114    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.7899    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.0685    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.3470    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.6255    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.9040    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.1825    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.4611    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7396    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.0181    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.1007    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.3793    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.6578    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.9363    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.2148    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.4933    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7718    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0504    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.3289    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.6074    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.8859    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.1644    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.4430    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.7215    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   19.2653   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   18.5438    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.8223   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.1008    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.3794   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.6579    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.9364   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.2149    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.4934   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.7720    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.0505   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.3290    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.6075   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.8860    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.1645   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4431    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.7216   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.0001    9.6076    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  2  8  1  6  0  0  0
  2  7  1  1  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  6  2  0  0  0  0
  5 12  1  0  0  0  0
  8  9  1  0  0  0  0
  9 10  2  0  0  0  0
  9 11  1  0  0  0  0
  1 13  1  0  0  0  0
 13 14  1  0  0  0  0
 14 15  1  0  0  0  0
 14 16  2  0  0  0  0
 11 17  1  0  0  0  0
 17 18  1  0  0  0  0
 18 19  1  0  0  0  0
 19 20  1  0  0  0  0
 20 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  2  0  0  0  0
 24 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  2  0  0  0  0
 27 28  1  0  0  0  0
 28 29  1  0  0  0  0
 29 30  1  0  0  0  0
 30 31  1  0  0  0  0
 12 32  1  0  0  0  0
 32 33  1  0  0  0  0
 33 34  1  0  0  0  0
 34 35  1  0  0  0  0
 35 36  1  0  0  0  0
 36 37  1  0  0  0  0
 37 38  1  0  0  0  0
 38 39  2  0  0  0  0
 39 40  1  0  0  0  0
 40 41  1  0  0  0  0
 41 42  1  0  0  0  0
 42 43  1  0  0  0  0
 43 44  1  0  0  0  0
 44 45  1  0  0  0  0
 45 46  1  0  0  0  0
 15 47  1  0  0  0  0
 47 48  1  0  0  0  0
 48 49  1  0  0  0  0
 49 50  1  0  0  0  0
 50 51  1  0  0  0  0
 51 52  1  0  0  0  0
 52 53  1  0  0  0  0
 53 54  1  0  0  0  0
 54 55  1  0  0  0  0
 55 56  1  0  0  0  0
 56 57  1  0  0  0  0
 57 58  1  0  0  0  0
 58 59  1  0  0  0  0
 59 60  1  0  0  0  0
 60 61  1  0  0  0  0
 61 62  1  0  0  0  0
 62 63  1  0  0  0  0
 63 64  1  0  0  0  0
M  END

> <LM_ID>
LMGL03010233

> <NAME>
TG(17:1(9Z)/17:2(9Z,12Z)/20:0)[iso6]

> <SYSTEMATIC_NAME>
1-(9Z-heptadecenoyl)-2-(9Z,12Z-heptadecadienoyl)-3-eicosanoyl-sn-glycerol

> <CATEGORY>
Glycerolipids [GL]

> <MAIN_CLASS>
Triradylglycerols [GL03]

> <SUB_CLASS>
Triacylglycerols [GL0301]

> <EXACT_MASS>
884.783290

> <FORMULA>
C57H104O6

> <INCHI_KEY>
PMQJCWRMENJRNL-INWYVWJNSA-N

> <INCHI>
InChI=1S/C57H104O6/c1-4-7-10-13-16-19-22-25-28-29-30-33-35-38-41-44-47-50-56(59)62-53-54(63-57(60)51-48-45-42-39-36-32-27-24-21-18-15-12-9-6-3)52-61-55(58)49-46-43-40-37-34-31-26-23-20-17-14-11-8-5-2/h15,18,23-24,26-27,54H,4-14,16-17,19-22,25,28-53H2,1-3H3/b18-15-,26-23-,27-24-/t54-/m1/s1

> <SMILES>
C(OC(=O)CCCCCCCCCCCCCCCCCCC)[C@]([H])(OC(CCCCCCC/C=C\C/C=C\CCCC)=O)COC(CCCCCCC/C=C\CCCCCCC)=O

> <ABBREVIATION>
TG 54:3

> <SYNONYMS>
TG(17:1/17:2/20:0)[iso6]; TG(54:3); TG(17:1_17:2_20:0)

> <PUBCHEM_CID>
9544198

$$$$
LMGL03010237
  LIPID_MAPS_STRUCTURE_DATABASE

 64 63  0  0  0  0  0  0  0  0999 V2000
   19.4016    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   18.6855    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.9698    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.2537    6.9572    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.5379    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.5379    8.1968    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   19.0993    6.2413    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   18.2718    6.2413    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   17.5559    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.5559    5.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.8401    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.8221    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   19.4016    8.1961    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   19.9861    8.7807    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   19.9861    9.6074    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   20.7021    8.3673    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   16.1188    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.3973    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.6758    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.9543    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.2329    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.5114    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.7899    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.0684    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.3469    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.6255    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.9040    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.1825    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.4610    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7396    5.8276    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.0181    6.2413    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.1007    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.3792    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.6577    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.9363    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.2148    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.4933    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7718    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0503    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.3289    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.6074    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.8859    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.1644    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.4430    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.7215    7.3695    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    6.9572    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   19.2652   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   18.5437    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.8223   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.1008    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.3793   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.6578    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.9363   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.2149    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.4934   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.7719   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.0504    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.3290   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.6075    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.8860   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.1645    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4431   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.7216    9.6075    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.0001   10.0208    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  2  8  1  6  0  0  0
  2  7  1  1  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  6  2  0  0  0  0
  5 12  1  0  0  0  0
  8  9  1  0  0  0  0
  9 10  2  0  0  0  0
  9 11  1  0  0  0  0
  1 13  1  0  0  0  0
 13 14  1  0  0  0  0
 14 15  1  0  0  0  0
 14 16  2  0  0  0  0
 11 17  1  0  0  0  0
 17 18  1  0  0  0  0
 18 19  1  0  0  0  0
 19 20  1  0  0  0  0
 20 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  2  0  0  0  0
 24 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  1  0  0  0  0
 27 28  1  0  0  0  0
 28 29  1  0  0  0  0
 29 30  1  0  0  0  0
 30 31  1  0  0  0  0
 12 32  1  0  0  0  0
 32 33  1  0  0  0  0
 33 34  1  0  0  0  0
 34 35  1  0  0  0  0
 35 36  1  0  0  0  0
 36 37  1  0  0  0  0
 37 38  1  0  0  0  0
 38 39  2  0  0  0  0
 39 40  1  0  0  0  0
 40 41  1  0  0  0  0
 41 42  1  0  0  0  0
 42 43  1  0  0  0  0
 43 44  1  0  0  0  0
 44 45  1  0  0  0  0
 45 46  1  0  0  0  0
 15 47  1  0  0  0  0
 47 48  1  0  0  0  0
 48 49  1  0  0  0  0
 49 50  1  0  0  0  0
 50 51  1  0  0  0  0
 51 52  1  0  0  0  0
 52 53  1  0  0  0  0
 53 54  1  0  0  0  0
 54 55  1  0  0  0  0
 55 56  2  0  0  0  0
 56 57  1  0  0  0  0
 57 58  1  0  0  0  0
 58 59  1  0  0  0  0
 59 60  1  0  0  0  0
 60 61  1  0  0  0  0
 61 62  1  0  0  0  0
 62 63  1  0  0  0  0
 63 64  1  0  0  0  0
M  END

> <LM_ID>
LMGL03010237

> <NAME>
TG(17:1(9Z)/17:1(9Z)/20:1(11Z))[iso3]

> <SYSTEMATIC_NAME>
1,2-di-(9Z-heptadecenoyl)-3-(11Z-eicosenoyl)-sn-glycerol

> <CATEGORY>
Glycerolipids [GL]

> <MAIN_CLASS>
Triradylglycerols [GL03]

> <SUB_CLASS>
Triacylglycerols [GL0301]

> <EXACT_MASS>
884.783290

> <FORMULA>
C57H104O6

> <INCHI_KEY>
GTMPLJHCEGNUNS-WULGQDQVSA-N

> <INCHI>
InChI=1S/C57H104O6/c1-4-7-10-13-16-19-22-25-28-29-30-33-35-38-41-44-47-50-56(59)62-53-54(63-57(60)51-48-45-42-39-36-32-27-24-21-18-15-12-9-6-3)52-61-55(58)49-46-43-40-37-34-31-26-23-20-17-14-11-8-5-2/h23-28,54H,4-22,29-53H2,1-3H3/b26-23-,27-24-,28-25-/t54-/m1/s1

> <SMILES>
C(OC(=O)CCCCCCCCC/C=C\CCCCCCCC)[C@]([H])(OC(CCCCCCC/C=C\CCCCCCC)=O)COC(CCCCCCC/C=C\CCCCCCC)=O

> <ABBREVIATION>
TG 54:3

> <SYNONYMS>
TG(17:1/17:1/20:1)[iso3]; TG(54:3); TG(17:1_17:1_20:1)

> <PUBCHEM_CID>
9544202

$$$$
LMSP02010004
  LIPID_MAPS_STRUCTURE_DATABASE

 40 39  0  0  0  0  0  0  0  0999 V2000
   16.9238    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.2114    7.6152    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.4988    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.3357    6.4925    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   16.5120    6.4925    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
   17.6366    7.6164    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   18.3492    7.2050    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   15.7657    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.7657    5.2475    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   15.0532    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.5993    8.2869    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   15.8143    8.3027    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   14.3355    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.6174    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.8993    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.1812    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.4631    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7449    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0268    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.3087    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.5906    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.8725    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.1544    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.4362    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.7181    6.0714    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    6.4831    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.7804    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.0622    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.3441    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.6260    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.9079    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.1898    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.4717    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.7535    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.0354    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.3173    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.5992    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.8811    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.1630    7.6151    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.4448    7.2050    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  1  5  1  6  0  0  0
  1  4  1  1  0  0  0
  6  1  1  0  0  0  0
  7  6  1  0  0  0  0
  8  9  2  0  0  0  0
  8 10  1  0  0  0  0
  8  5  1  0  0  0  0
  2 11  1  1  0  0  0
  2 12  1  6  0  0  0
 10 13  1  0  0  0  0
 13 14  1  0  0  0  0
 14 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 18  1  0  0  0  0
 18 19  1  0  0  0  0
 19 20  1  0  0  0  0
 20 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  1  0  0  0  0
 24 25  1  0  0  0  0
 25 26  1  0  0  0  0
  3 27  2  0  0  0  0
 27 28  1  0  0  0  0
 28 29  1  0  0  0  0
 29 30  1  0  0  0  0
 30 31  1  0  0  0  0
 31 32  1  0  0  0  0
 32 33  1  0  0  0  0
 33 34  1  0  0  0  0
 34 35  1  0  0  0  0
 35 36  1  0  0  0  0
 36 37  1  0  0  0  0
 37 38  1  0  0  0  0
 38 39  1  0  0  0  0
 39 40  1  0  0  0  0
M  END

> <LM_ID>
LMSP02010004

> <NAME>
Cer(d18:1/16:0)

> <SYSTEMATIC_NAME>
N-(hexadecanoyl)-sphing-4-enine

> <CATEGORY>
Sphingolipids [SP]

> <MAIN_CLASS>
Ceramides [SP02]

> <SUB_CLASS>
N-acylsphingosines (ceramides) [SP0201]

> <EXACT_MASS>
537.512094

> <FORMULA>
C34H67NO3

> <INCHI_KEY>
YDNKGFDKKRUKPY-TURZORIXSA-N

> <INCHI>
InChI=1S/C34H67NO3/c1-3-5-7-9-11-13-15-17-19-21-23-25-27-29-33(37)32(31-36)35-34(38)30-28-26-24-22-20-18-16-14-12-10-8-6-4-2/h27,29,32-33,36-37H,3-26,28,30-31H2,1-2H3,(H,35,38)/b29-27+/t32-,33+/m0/s1

> <SMILES>
[C@](CO)([H])(NC(CCCCCCCCCCCCCCC)=O)[C@]([H])(O)/C=C/CCCCCCCCCCCCC

> <ABBREVIATION>
Cer 34:1;O2

> <SYNONYMS>
C16 Cer; N-(hexadecanoyl)-ceramide; N-(palmitoyl)-ceramide; N-palmitoyl-sphingosine; Cer[NS]

> <PUBCHEM_CID>
5283564

> <HMDB_ID>
HMDB0004949

> <CHEBI_ID>
72959

> <SWISSLIPIDS_ID>
SLM:000000554

$$$$
LMSP02010036
  LIPID_MAPS_STRUCTURE_DATABASE

 40 39  0  0  0  0  0  0  0  0999 V2000
   19.7990    7.2046    0.0000 C   0  0  1  0  0  0  0  0  0  0  0  0
   19.0867    7.6147    0.0000 C   0  0  1  0  0  0  0  0  0  0  0  0
   18.3742    7.2046    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   20.2107    6.4923    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   19.3872    6.4923    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0
   20.5116    7.6159    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   21.2240    7.2046    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   18.6410    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   18.6410    5.2475    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   19.4745    8.2863    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   18.6897    8.3021    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   17.9232    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.2052    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.4873    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.7693    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.0514    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.3334    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.6154    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.8975    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.1795    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.4616    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7436    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0257    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.3077    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.5898    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.8718    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.1538    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.4359    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.7179    6.0713    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.0000    6.4828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   17.6560    7.6146    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.9380    7.2046    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   16.2200    7.6146    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   15.5021    7.2046    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.7841    7.6146    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.0662    7.2046    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.3482    7.6146    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.6303    7.2046    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.9123    7.6146    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.1944    7.2046    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  1  5  1  6  0  0  0
  1  4  1  1  0  0  0
  6  1  1  0  0  0  0
  7  6  1  0  0  0  0
  8  9  2  0  0  0  0
  8  5  1  0  0  0  0
  2 10  1  1  0  0  0
  2 11  1  6  0  0  0
  8 12  1  0  0  0  0
 12 13  1  0  0  0  0
 13 14  1  0  0  0  0
 14 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 18  1  0  0  0  0
 18 19  1  0  0  0  0
 19 20  1  0  0  0  0
 20 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  1  0  0  0  0
 24 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  1  0  0  0  0
 27 28  1  0  0  0  0
 28 29  1  0  0  0  0
 29 30  1  0  0  0  0
  3 31  2  0  0  0  0
 31 32  1  0  0  0  0
 32 33  1  0  0  0  0
 33 34  1  0  0  0  0
 34 35  1  0  0  0  0
 35 36  1  0  0  0  0
 36 37  1  0  0  0  0
 37 38  1  0  0  0  0
 38 39  1  0  0  0  0
 39 40  1  0  0  0  0
M  END

> <LM_ID>
LMSP02010036

> <NAME>
Cer(d14:1/20:0)

> <SYSTEMATIC_NAME>
N-(eicosanoyl)-tetradecasphing-4-enine

> <CATEGORY>
Sphingolipids [SP]

> <MAIN_CLASS>
Ceramides [SP02]

> <SUB_CLASS>
N-acylsphingosines (ceramides) [SP0201]

> <EXACT_MASS>
537.512094

> <FORMULA>
C34H67NO3

> <INCHI_KEY>
DLTXHYMYPKOZOA-TURZORIXSA-N

> <INCHI>
InChI=1S/C34H67NO3/c1-3-5-7-9-11-13-14-15-16-17-18-19-20-22-24-26-28-30-34(38)35-32(31-36)33(37)29-27-25-23-21-12-10-8-6-4-2/h27,29,32-33,36-37H,3-26,28,30-31H2,1-2H3,(H,35,38)/b29-27+/t32-,33+/m0/s1

> <SMILES>
[C@](CO)([H])(NC(CCCCCCCCCCCCCCCCCCC)=O)[C@]([H])(O)/C=C/CCCCCCCCC

> <ABBREVIATION>
Cer 34:1;O2

> <SYNONYMS>
Cer(d14:1(4E)/20:0); Cer[NS]

> <PUBCHEM_CID>
11092732

> <CHEBI_ID>
179989

> <SWISSLIPIDS_ID>
SLM:000397291

$$$$
LMST01010001
  LIPID_MAPS_STRUCTURE_DATABASE

 33 36  0  0  0  0  0  0  0  0999 V2000
    9.0635    6.4671    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.0590    8.1037    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.3505    7.6906    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.3577    6.8727    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.7751    7.6987    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.7722    6.8801    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.1892    6.8751    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.1921    7.6938    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.4850    8.1081    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.0612    7.2698    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    9.7492    8.5704    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.4762    8.9040    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.1812    9.3042    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.4861    9.7068    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   11.8717    8.9023    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.5651    9.2993    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.2556    8.8975    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.9489    9.2945    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.7713    6.0846    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   13.2556    8.0895    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6535    6.4671    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6535    5.6531    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.3577    5.2475    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.0635    5.6531    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.9538    6.8711    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.2541    6.4671    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.2541    5.6592    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.9538    5.2553    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6535    7.2750    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.5544    5.2553    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   11.1832    8.4172    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    9.8525    9.2963    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.3577    6.0648    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  4  1  0  0  0  0
  1  6  1  0  0  0  0
  5  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  5  6  1  0  0  0  0
  7  8  1  0  0  0  0
  8  9  1  0  0  0  0
  9  5  1  0  0  0  0
  6  7  1  0  0  0  0
  1 10  1  1  0  0  0
  5 11  1  1  0  0  0
  9 12  1  0  0  0  0
 12 13  1  0  0  0  0
 12 14  1  1  0  0  0
 13 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 18  1  0  0  0  0
  6 19  1  6  0  0  0
 17 20  1  0  0  0  0
  4 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  2  0  0  0  0
 23 24  1  0  0  0  0
 24  1  1  0  0  0  0
 21 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  1  0  0  0  0
 27 28  1  0  0  0  0
 28 22  1  0  0  0  0
 21 29  1  1  0  0  0
 27 30  1  1  0  0  0
  9 31  1  6  0  0  0
 12 32  1  6  0  0  0
  4 33  1  6  0  0  0
M  END

> <LM_ID>
LMST01010001

> <NAME>
Cholesterol

> <SYSTEMATIC_NAME>
cholest-5-en-3beta-ol

> <CATEGORY>
Sterol Lipids [ST]

> <MAIN_CLASS>
Sterols [ST01]

> <SUB_CLASS>
Cholesterol and derivatives [ST0101]

> <EXACT_MASS>
386.354865

> <FORMULA>
C27H46O

> <INCHI_KEY>
HVYWMOMLDIMFJA-DPAQBDIFSA-N

> <INCHI>
InChI=1S/C27H46O/c1-18(2)7-6-8-19(3)23-11-12-24-22-10-9-20-17-21(28)13-15-26(20,4)25(22)14-16-27(23,24)5/h9,18-19,21-25,28H,6-8,10-17H2,1-5H3/t19-,21+,22+,23-,24+,25+,26+,27-/m1/s1

> <SMILES>
[C@]12(CC=C3C[C@@H](O)CC[C@]3(C)[C@@]1([H])CC[C@]1(C)[C@@]([H])([C@@](C)([H])CCCC(C)C)CC[C@@]21[H])[H]

> <ABBREVIATION>
ST 27:1;O

> <SYNONYMS>
Cholesterol; Cholest-5-en-3-ol; (3beta)-Cholest-5-en-3-ol; Cholesteryl alcohol

> <PUBCHEM_CID>
5997

> <KEGG_ID>
C00187

> <HMDB_ID>
HMDB0000067

> <CHEBI_ID>
16113

> <LIPIDBANK_ID>
SST9061

> <SWISSLIPIDS_ID>
SLM:000000287

$$$$
LMST01010066
  LIPID_MAPS_STRUCTURE_DATABASE

 32 35  0  0  0  0  0  0  0  0999 V2000
    6.8872    7.1894    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.1102    6.7407    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.1102    5.8436    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.8872    5.3949    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6643    5.8436    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4413    5.3949    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.2184    5.8436    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.2184    6.7407    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4413    7.1894    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6643    6.7407    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4413    8.0866    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.2184    8.5353    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.9953    8.0866    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.9953    7.1894    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.5494    7.1894    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.5494    8.0866    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7724    8.5353    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.9953    8.7821    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.6643    7.3690    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.7724    9.2531    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.0417    9.4488    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.3940    9.6119    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.0156    9.2531    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.6373    9.6119    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.2588    9.2531    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.8805    9.6119    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.2588    8.6471    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.2756    8.8258    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   10.7724   10.0185    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    5.5544    5.5227    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    7.6643    5.2475    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    9.9953    6.4932    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  7  1  0  0  0  0
  7  8  1  0  0  0  0
  8  9  2  0  0  0  0
  9 11  1  0  0  0  0
 11 12  1  0  0  0  0
 12 13  1  0  0  0  0
 13 14  1  0  0  0  0
 14 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 20  1  0  0  0  0
 20 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  1  0  0  0  0
 24 25  2  0  0  0  0
 25 26  1  0  0  0  0
 25 27  1  0  0  0  0
  1 10  1  0  0  0  0
  5 10  1  0  0  0  0
  9 10  1  0  0  0  0
  8 14  1  0  0  0  0
 13 17  1  0  0  0  0
 13 18  1  1  0  0  0
 10 19  1  1  0  0  0
 20 21  1  6  0  0  0
 17 28  1  6  0  0  0
 20 29  1  1  0  0  0
  3 30  1  1  0  0  0
  5 31  1  6  0  0  0
 14 32  1  6  0  0  0
M  END

> <LM_ID>
LMST01010066

> <NAME>
Zymosterol

> <SYSTEMATIC_NAME>
5alpha-cholesta-8,24-dien-3beta-ol

> <CATEGORY>
Sterol Lipids [ST]

> <MAIN_CLASS>
Sterols [ST01]

> <SUB_CLASS>
Cholesterol and derivatives [ST0101]

> <EXACT_MASS>
384.339215

> <FORMULA>
C27H44O

> <INCHI_KEY>
CGSJXLIKVBJVRY-XTGBIJOFSA-N

> <INCHI>
InChI=1S/C27H44O/c1-18(2)7-6-8-19(3)23-11-12-24-22-10-9-20-17-21(28)13-15-26(20,4)25(22)14-16-27(23,24)5/h7,19-21,23-24,28H,6,8-17H2,1-5H3/t19-,20+,21+,23-,24+,26+,27-/m1/s1

> <SMILES>
C1[C@]2(C)C3CC[C@]4(C)[C@@]([H])([C@]([H])(C)CC/C=C(\C)/C)CC[C@@]4([H])C=3CC[C@@]2([H])C[C@@H](O)C1

> <ABBREVIATION>
ST 27:2;O

> <PUBCHEM_CID>
92746

> <KEGG_ID>
C05437

> <HMDB_ID>
HMDB0006271

> <CHEBI_ID>
18252

> <LIPIDBANK_ID>
SST9103

> <SWISSLIPIDS_ID>
SLM:000000319

$$$$
LMST01030121
  LIPID_MAPS_STRUCTURE_DATABASE

 38 41  0  0  0  0  0  0  0  0999 V2000
    9.1735    7.0762    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.1688    8.7641    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4381    8.3380    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4455    7.4945    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.9074    8.3464    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.9044    7.5021    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.3658    7.4970    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.3688    8.3414    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.6395    8.7686    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.1711    7.9041    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    9.8806    9.2454    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.6305    9.5895    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   11.3575   10.0022    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   10.6406   10.4174    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   12.0696    9.5877    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   12.7848    9.9972    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   13.4970    9.5828    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   14.2119    9.9922    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.9034    6.6817    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   13.4970    8.7494    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.7192    7.0762    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.7192    6.2367    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4455    5.8184    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    9.1735    6.2367    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.9976    7.4929    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.2760    7.0762    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.2760    6.2429    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.9976    5.8264    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.7192    7.9094    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.5544    5.8264    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   11.3596    9.0874    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    9.9872    9.9941    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    8.4455    6.6613    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   11.3575   10.6961    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   12.0696    8.9860    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   12.7848   10.6769    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    7.7192    5.5888    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    8.4455    5.2475    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  4  1  0  0  0  0
  1  6  1  0  0  0  0
  5  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  5  6  1  0  0  0  0
  7  8  1  0  0  0  0
  8  9  1  0  0  0  0
  9  5  1  0  0  0  0
  6  7  1  0  0  0  0
  1 10  1  1  0  0  0
  5 11  1  1  0  0  0
  9 12  1  0  0  0  0
 12 13  1  0  0  0  0
 12 14  1  1  0  0  0
 13 15  1  0  0  0  0
 15 16  1  0  0  0  0
 16 17  1  0  0  0  0
 17 18  1  0  0  0  0
  6 19  1  6  0  0  0
 17 20  1  0  0  0  0
  4 21  1  0  0  0  0
 21 22  1  0  0  0  0
 22 23  1  0  0  0  0
 23 24  1  0  0  0  0
 24  1  1  0  0  0  0
 21 25  1  0  0  0  0
 25 26  1  0  0  0  0
 26 27  1  0  0  0  0
 27 28  1  0  0  0  0
 28 22  1  0  0  0  0
 21 29  1  1  0  0  0
 27 30  1  1  0  0  0
  9 31  1  6  0  0  0
 12 32  1  6  0  0  0
  4 33  1  6  0  0  0
 13 34  1  1  0  0  0
 15 35  1  1  0  0  0
 16 36  1  1  0  0  0
 22 37  1  6  0  0  0
 23 38  2  0  0  0  0
M  END

> <LM_ID>
LMST01030121

> <NAME>
Teasterone

> <SYSTEMATIC_NAME>
6-oxo-5alpha-campestan-3beta,22R,23R-triol

> <CATEGORY>
Sterol Lipids [ST]

> <MAIN_CLASS>
Sterols [ST01]

> <SUB_CLASS>
Ergosterols and C24-methyl derivatives [ST0103]

> <EXACT_MASS>
448.355260

> <FORMULA>
C28H48O4

> <INCHI_KEY>
SBSXXCCMIWEPEE-GZKYLSGOSA-N

> <INCHI>
InChI=1S/C28H48O4/c1-15(2)16(3)25(31)26(32)17(4)20-7-8-21-19-14-24(30)23-13-18(29)9-11-28(23,6)22(19)10-12-27(20,21)5/h15-23,25-26,29,31-32H,7-14H2,1-6H3/t16-,17-,18-,19-,20+,21-,22-,23+,25+,26+,27+,28+/m0/s1

> <SMILES>
[C@]12(CC(=O)[C@@]3([H])C[C@@H](O)CC[C@]3(C)[C@@]1([H])CC[C@]1(C)[C@@]([H])([C@@](C)([H])[C@@H](O)[C@H](O)[C@@H](C)C(C)C)CC[C@@]21[H])[H]

> <ABBREVIATION>
ST 28:1;O4

> <PUBCHEM_CID>
13475125

> <CHEBI_ID>
26863

"""  # noqa: E501
