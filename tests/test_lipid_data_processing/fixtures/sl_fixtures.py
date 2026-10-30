"""Module concerning SwissLipids fixtures."""

import logging

from pathlib import Path

import pandas as pd
import pytest

from _pytest.tmpdir import TempPathFactory

from lipid_data_processing.databases.swiss_lipids import SwissLipids

from tests.test_lipid_data_processing.util.lipid_description import (
    LipidCollection,
    LipidDescription,
    SLLipid,
    ParsedLipid,
)

logger: logging.Logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def sl_tmp_file_path(tmp_path_factory: TempPathFactory) -> Path:
    sl_tmp_file_path: Path = tmp_path_factory.mktemp("sl").joinpath("sl.csv")

    with open(sl_tmp_file_path, "w") as file:
        file.write(_SL_CSV_STR)

    return sl_tmp_file_path


@pytest.fixture(scope="session")
def sl_lipids(
    slm_000117321: LipidDescription,
    slm_000117356: LipidDescription,
    slm_000012707: LipidDescription,
    slm_000012703: LipidDescription,
    slm_000012858: LipidDescription,
    slm_000395441: LipidDescription,
    slm_000395404: LipidDescription,
    slm_000399188: LipidDescription,
) -> LipidCollection:
    return LipidCollection(
        [
            slm_000117321,
            slm_000117356,
            slm_000012707,
            slm_000012703,
            slm_000012858,
            slm_000395441,
            slm_000395404,
            slm_000399188,
        ]
    )


@pytest.fixture(scope="session")
def sl_df(sl_lipids: LipidCollection) -> pd.DataFrame:
    return sl_lipids.to_sl_df()


@pytest.fixture(scope="session")
def swiss_lipids(sl_df: pd.DataFrame) -> SwissLipids:
    return SwissLipids(sl_df)


@pytest.fixture(scope="session")
def sl_parsed_df(sl_lipids: LipidCollection) -> pd.DataFrame:
    return sl_lipids.to_sl_parsed_df()


@pytest.fixture(scope="session")
def slm_000117321() -> LipidDescription:
    original_name: str = "DG(12:0/12:0/0:0)"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000117321",
        name=original_name,
        mass=456.698792,
        smiles="CCCCCCCCCCCC(=O)OC[C@H](CO)OC(=O)CCCCCCCCCCC",
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 12:0/12:0/0:0",
        level="FULL_STRUCTURE",
        category="GL",
        class_="DG",
        species="DG 24:0",
        molecular_species="DG 12:0_12:0",
        sn_position="DG 12:0/12:0/0:0",
        structure_defined="DG 12:0/12:0/0:0",
        full_structure="DG 12:0/12:0/0:0",
        complete_structure="UNDEFINED",
        fa1="12:0",
        fa2="12:0",
        fa3="0:0",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000117356() -> LipidDescription:
    original_name: str = "DG(12:0/14:1(9Z)/0:0)"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000117356",
        name=original_name,
        mass=482.736115,
        smiles=r"CCCCCCCCCCCC(=O)OC[C@H](CO)OC(=O)CCCCCCC\C=C/CCCC",
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="DG 12:0/14:1(9Z)/0:0",
        level="FULL_STRUCTURE",
        category="GL",
        class_="DG",
        species="DG 26:1",
        molecular_species="DG 12:0_14:1",
        sn_position="DG 12:0/14:1/0:0",
        structure_defined="DG 12:0/14:1(9)/0:0",
        full_structure="DG 12:0/14:1(9Z)/0:0",
        complete_structure="UNDEFINED",
        fa1="12:0",
        fa2="14:1(9Z)",
        fa3="0:0",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000012703() -> LipidDescription:
    original_name: str = "PC(10:0/20:4(8Z,11Z,14Z,17Z))"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000012703",
        name=original_name,
        mass=697.922180,
        smiles=(
            r"CCCCCCCCCC(=O)OC[C@H](COP([O-])(=O)OCC[N+](C)(C)C)OC(=O)CCCCCC"
            r"\C=C/C\C=C/C\C=C/C\C=C/CC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="PC 10:0/20:4(8Z,11Z,14Z,17Z)",
        level="FULL_STRUCTURE",
        category="GP",
        class_="PC",
        species="PC 30:4",
        molecular_species="PC 10:0_20:4",
        sn_position="PC 10:0/20:4",
        structure_defined="PC 10:0/20:4(8,11,14,17)",
        full_structure="PC 10:0/20:4(8Z,11Z,14Z,17Z)",
        complete_structure="UNDEFINED",
        fa1="10:0",
        fa2="20:4(8Z,11Z,14Z,17Z)",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000012707() -> LipidDescription:
    original_name: str = "PC(10:0/24:4(9Z,12Z,15Z,18Z))"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000012707",
        name=original_name,
        mass=754.028503,
        smiles=(
            r"CCCCCCCCCC(=O)OC[C@H](COP([O-])(=O)OCC[N+](C)(C)C)OC(=O)CCCCCCC"
            r"\C=C/C\C=C/C\C=C/C\C=C/CCCCC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="PC 10:0/24:4(9Z,12Z,15Z,18Z)",
        level="FULL_STRUCTURE",
        category="GP",
        class_="PC",
        species="PC 34:4",
        molecular_species="PC 10:0_24:4",
        sn_position="PC 10:0/24:4",
        structure_defined="PC 10:0/24:4(9,12,15,18)",
        full_structure="PC 10:0/24:4(9Z,12Z,15Z,18Z)",
        complete_structure="UNDEFINED",
        fa1="10:0",
        fa2="24:4(9Z,12Z,15Z,18Z)",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000012858() -> LipidDescription:
    original_name: str = "PC(12:0/22:4(7Z,10Z,13Z,16Z))"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000012858",
        name=original_name,
        mass=754.028503,
        smiles=(
            r"CCCCCCCCCCCC(=O)OC[C@H](COP([O-])(=O)OCC[N+](C)(C)C)OC(=O)CCCCC"
            r"\C=C/C\C=C/C\C=C/C\C=C/CCCCC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="PC 12:0/22:4(7Z,10Z,13Z,16Z)",
        level="FULL_STRUCTURE",
        category="GP",
        class_="PC",
        species="PC 34:4",
        molecular_species="PC 12:0_22:4",
        sn_position="PC 12:0/22:4",
        structure_defined="PC 12:0/22:4(7,10,13,16)",
        full_structure="PC 12:0/22:4(7Z,10Z,13Z,16Z)",
        complete_structure="UNDEFINED",
        fa1="12:0",
        fa2="22:4(7Z,10Z,13Z,16Z)",
        fa3="N/A",
        fa4="N/A",
        lcb="N/A",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000395441() -> LipidDescription:
    original_name: str = "GlcCer(d18:1(4E)/20:3(11Z,14Z,17Z))"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000395441",
        name=original_name,
        mass=750.100000,
        smiles=(
            r"CCCCCCCCCCCCC\C=C\[C@@H](O)[C@H](CO[C@@H]1O[C@H](CO)[C@@H](O)"
            r"[C@H](O)[C@H]1O)NC(=O)CCCCCCCCC\C=C/C\C=C/C\C=C/CC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="GlcCer(1) 18:1(4E);3OH/20:3(11Z,14Z,17Z)",
        level="FULL_STRUCTURE",
        category="SP",
        class_="GlcCer",
        species="GlcCer 38:4;O2",
        molecular_species="GlcCer 18:1;O2/20:3",
        sn_position="GlcCer 18:1;O2/20:3",
        structure_defined="GlcCer 18:1(4);OH/20:3(11,14,17)",
        full_structure="GlcCer(1) 18:1(4E);3OH/20:3(11Z,14Z,17Z)",
        complete_structure="UNDEFINED",
        fa1="20:3(11Z,14Z,17Z)",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="18:1(4E);3OH",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000395404() -> LipidDescription:
    original_name: str = "GalCer(d18:1(4E)/20:3(8Z,11Z,14Z))"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000395404",
        name=original_name,
        mass=750.100000,
        smiles=(
            r"CCCCCCCCCCCCC\C=C\[C@@H](O)[C@H](CO[C@@H]1O[C@H]"
            r"(CO)[C@H](O)[C@H](O)[C@H]1O)NC(=O)CCCCCC\C=C/C\C=C/C\C=C/CCCCC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="GalCer(1) 18:1(4E);3OH/20:3(8Z,11Z,14Z)",
        level="FULL_STRUCTURE",
        category="SP",
        class_="GalCer",
        species="GalCer 38:4;O2",
        molecular_species="GalCer 18:1;O2/20:3",
        sn_position="GalCer 18:1;O2/20:3",
        structure_defined="GalCer 18:1(4);OH/20:3(8,11,14)",
        full_structure="GalCer(1) 18:1(4E);3OH/20:3(8Z,11Z,14Z)",
        complete_structure="UNDEFINED",
        fa1="20:3(8Z,11Z,14Z)",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="18:1(4E);3OH",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


@pytest.fixture(scope="session")
def slm_000399188() -> LipidDescription:
    original_name: str = "LacCer(d18:0/18:1(6Z))"

    sl_lipid: SLLipid = SLLipid(
        index="SLM:000399188",
        name=original_name,
        mass=890.235000,
        smiles=(
            r"CCCCCCCCCCCCCCC[C@@H](O)[C@H](CO[C@@H]1O[C@H](CO)[C@@H]"
            r"(O[C@@H]2O[C@H](CO)[C@H](O)[C@H](O)[C@H]2O)[C@H](O)[C@H]1O)"
            r"NC(=O)CCCC\C=C/CCCCCCCCCCC"
        ),
    )

    parsed_lipid: ParsedLipid = ParsedLipid(
        original_name=original_name,
        parsed_name="LacCer(1) 18:0;3OH/18:1(6Z)",
        level="FULL_STRUCTURE",
        category="SP",
        class_="LacCer",
        species="LacCer 36:1;O2",
        molecular_species="LacCer 18:0;O2/18:1",
        sn_position="LacCer 18:0;O2/18:1",
        structure_defined="LacCer 18:0;OH/18:1(6)",
        full_structure="LacCer(1) 18:0;3OH/18:1(6Z)",
        complete_structure="UNDEFINED",
        fa1="18:1(6Z)",
        fa2="N/A",
        fa3="N/A",
        fa4="N/A",
        lcb="18:0;3OH",
    )

    lipid_description: LipidDescription = LipidDescription(
        original_name=original_name,
        parsed_lipid=parsed_lipid,
        sl_lipid=sl_lipid,
        index=sl_lipid.index,
    )

    return lipid_description


# * DB SOURCE FILE STRING -----------------------------------------------------


_SL_CSV_STR: str = r"""
Lipid ID	Level	Name	Abbreviation*	Synonyms*	Lipid class*	Parent	Components*	SMILES (pH7.3)	InChI (pH7.3)	InChI key (pH7.3)	Formula (pH7.3)	Charge (pH7.3)	Mass (pH7.3)	Exact Mass (neutral form)	Exact m/z of [M.]+	Exact m/z of [M+H]+	Exact m/z of [M+K]+	Exact m/z of [M+Na]+	Exact m/z of [M+Li]+	Exact m/z of [M+NH4]+	Exact m/z of [M-H]-	Exact m/z of [M+Cl]-	Exact m/z of [M+OAc]-	CHEBI	LIPID MAPS	HMDB	MetaNetX	PMID
SLM:000117321	Isomeric subspecies	1,2-didodecanoyl-sn-glycerol	DG(12:0/12:0/0:0)	Diacylglycerol (12:0/12:0/0:0)	SLM:000000262	SLM:000332323	SLM:000000719 (sn1 or sn2)	CCCCCCCCCCCC(=O)OC[C@H](CO)OC(=O)CCCCCCCCCCC	InChI=1S/C27H52O5/c1-3-5-7-9-11-13-15-17-19-21-26(29)31-24-25(23-28)32-27(30)22-20-18-16-14-12-10-8-6-4-2/h25,28H,3-24H2,1-2H3/t25-/m0/s1	InChIKey=OQQOAWVKVDAJOI-VWLOTQADSA-N	C27H52O5	0	456.698792	456.381470	456.380920	457.388763	495.344635	479.370697	463.396942	474.415314	455.374207	491.350891	515.395325		LMGL02010323		MNXM507729
SLM:000117356	Isomeric subspecies	1-dodecanoyl-2-(9Z-tetradecenoyl)-sn-glycerol	DG(12:0/14:1(9Z)/0:0)	Diacylglycerol (12:0/14:1(9Z)/0:0)	SLM:000000262		SLM:000000719 (sn1) / SLM:000000856 (sn2)	CCCCCCCCCCCC(=O)OC[C@H](CO)OC(=O)CCCCCCC\C=C/CCCC	InChI=1S/C29H54O5/c1-3-5-7-9-11-13-14-16-18-20-22-24-29(32)34-27(25-30)26-33-28(31)23-21-19-17-15-12-10-8-6-4-2/h9,11,27,30H,3-8,10,12-26H2,1-2H3/b11-9-/t27-/m0/s1	InChIKey=ARFFFIALGZLPMU-RUNMITEXSA-N	C29H54O5	0	482.736115	482.397125	482.396576	483.404388	521.360291	505.386353	489.412567	500.430939	481.389862	517.366516	541.410950				MNXM351871
SLM:000012707	Isomeric subspecies	1-decanoyl-2-(9Z,12Z,15Z,18Z-tetracosatetraenoyl)-sn-glycero-3-phosphocholine	PC(10:0/24:4(9Z,12Z,15Z,18Z))	Phosphatidylcholine (10:0/24:4(9Z,12Z,15Z,18Z))	SLM:000000261	SLM:000087779	SLM:000000855 (sn1) / SLM:000001209 (sn2)	CCCCCCCCCC(=O)OC[C@H](COP([O-])(=O)OCC[N+](C)(C)C)OC(=O)CCCCCCC\C=C/C\C=C/C\C=C/C\C=C/CCCCC	InChI=1S/C42H76NO8P/c1-6-8-10-12-14-15-16-17-18-19-20-21-22-23-24-25-26-27-29-31-33-35-42(45)51-40(39-50-52(46,47)49-37-36-43(3,4)5)38-48-41(44)34-32-30-28-13-11-9-7-2/h14-15,17-18,20-21,23-24,40H,6-13,16,19,22,25-39H2,1-5H3/b15-14-,18-17-,21-20-,24-23-/t40-/m1/s1	InChIKey=JOYZYCBWNLXBSO-VZVUCAHISA-N	C42H76NO8P	0	754.028503	753.530884	753.530334	754.538147	792.494019	776.520081	760.546326	771.564697		788.500244	812.544678				MNXM345534
SLM:000012703	Isomeric subspecies	1-decanoyl-2-(8Z,11Z,14Z,17Z-eicosatetraenoyl)-sn-glycero-3-phosphocholine	PC(10:0/20:4(8Z,11Z,14Z,17Z))	Phosphatidylcholine (10:0/20:4(8Z,11Z,14Z,17Z))	SLM:000000261	SLM:000087767	SLM:000000855 (sn1) / SLM:000001206 (sn2)	CCCCCCCCCC(=O)OC[C@H](COP([O-])(=O)OCC[N+](C)(C)C)OC(=O)CCCCCC\C=C/C\C=C/C\C=C/C\C=C/CC	InChI=1S/C38H68NO8P/c1-6-8-10-12-14-15-16-17-18-19-20-21-22-23-25-27-29-31-38(41)47-36(35-46-48(42,43)45-33-32-39(3,4)5)34-44-37(40)30-28-26-24-13-11-9-7-2/h8,10,14-15,17-18,20-21,36H,6-7,9,11-13,16,19,22-35H2,1-5H3/b10-8-,15-14-,18-17-,21-20-/t36-/m1/s1	InChIKey=YLPGLRJAKOZECE-DFNJXGBQSA-N	C38H68NO8P	0	697.922180	697.468262	697.467712	698.475525	736.431396	720.457458	704.483704	715.502075		732.437683	756.482117				MNXM345478
SLM:000012858	Isomeric subspecies	1-dodecanoyl-2-(7Z,10Z,13Z,16Z-docosatetraenoyl)-sn-glycero-3-phosphocholine	PC(12:0/22:4(7Z,10Z,13Z,16Z))	Phosphatidylcholine (12:0/22:4(7Z,10Z,13Z,16Z))	SLM:000000261	SLM:000087839	SLM:000000719 (sn1) / SLM:000001124 (sn2)	CCCCCCCCCCCC(=O)OC[C@H](COP([O-])(=O)OCC[N+](C)(C)C)OC(=O)CCCCC\C=C/C\C=C/C\C=C/C\C=C/CCCCC	InChI=1S/C42H76NO8P/c1-6-8-10-12-14-16-17-18-19-20-21-22-23-24-25-27-29-31-33-35-42(45)51-40(39-50-52(46,47)49-37-36-43(3,4)5)38-48-41(44)34-32-30-28-26-15-13-11-9-7-2/h14,16,18-19,21-22,24-25,40H,6-13,15,17,20,23,26-39H2,1-5H3/b16-14-,19-18-,22-21-,25-24-/t40-/m1/s1	InChIKey=YOKRROJLYKOJNI-SRHQVDMPSA-N	C42H76NO8P	0	754.028503	753.530884	753.530334	754.538147	792.494019	776.520081	760.546326	771.564697		788.500244	812.544678		LMGP01011337		MNXM69086
SLM:000395441	Isomeric subspecies	N-(11Z,14Z,17Z-eicoastrienoyl)-1-O-beta-D-glucosyl-sphing-4-enine	GlcCer(d18:1(4E)/20:3(11Z,14Z,17Z))	Glucosyl ceramide (d18:1(4E)/20:3(11Z,14Z,17Z))	SLM:000000972	SLM:000393873	SLM:000001108 (n-acyl)	CCCCCCCCCCCCC\C=C\[C@@H](O)[C@H](CO[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O)NC(=O)CCCCCCCCC\C=C/C\C=C/C\C=C/CC	InChI=1S/C44H79NO8/c1-3-5-7-9-11-13-15-17-18-19-20-22-24-26-28-30-32-34-40(48)45-37(36-52-44-43(51)42(50)41(49)39(35-46)53-44)38(47)33-31-29-27-25-23-21-16-14-12-10-8-6-4-2/h5,7,11,13,17-18,31,33,37-39,41-44,46-47,49-51H,3-4,6,8-10,12,14-16,19-30,32,34-36H2,1-2H3,(H,45,48)/b7-5-,13-11-,18-17-,33-31+/t37-,38+,39+,41+,42-,43+,44+/m0/s1	InChIKey=RDOGLYXAYOWLLL-XYMGBUEASA-N	C44H79NO8	0	750.100000	749.580569	749.580020	750.587845	788.543727	772.569790	756.596024	767.614394	748.573292	784.549970	808.594421				MNXM571892
SLM:000395404	Isomeric subspecies	N-(8Z,11Z,14Z-eicosatrienoyl)-1-O-beta-D-galactosyl-sphing-4-enine	GalCer(d18:1(4E)/20:3(8Z,11Z,14Z))	Galactosyl ceramide (d18:1(4E)/20:3(8Z,11Z,14Z))	SLM:000000926	SLM:000393873	SLM:000000928 (n-acyl)	CCCCCCCCCCCCC\C=C\[C@@H](O)[C@H](CO[C@@H]1O[C@H](CO)[C@H](O)[C@H](O)[C@H]1O)NC(=O)CCCCCC\C=C/C\C=C/C\C=C/CCCCC	InChI=1S/C44H79NO8/c1-3-5-7-9-11-13-15-17-18-19-20-22-24-26-28-30-32-34-40(48)45-37(36-52-44-43(51)42(50)41(49)39(35-46)53-44)38(47)33-31-29-27-25-23-21-16-14-12-10-8-6-4-2/h11,13,17-18,20,22,31,33,37-39,41-44,46-47,49-51H,3-10,12,14-16,19,21,23-30,32,34-36H2,1-2H3,(H,45,48)/b13-11-,18-17-,22-20-,33-31+/t37-,38+,39+,41-,42-,43+,44+/m0/s1	InChIKey=ZCOJPGOZIZOJFQ-AHJPBXSUSA-N	C44H79NO8	0	750.100000	749.580569	749.580020	750.587845	788.543727	772.569790	756.596024	767.614394	748.573292	784.549970	808.594421				MNXM575529
SLM:000399188	Isomeric subspecies	N-(6Z-octadecenoyl)-beta-D-galactosyl-(1->4)-beta-D-glucosyl-(1->1)-sphinganine	LacCer(d18:0/18:1(6Z))	Lactosyl ceramide (d18:0/18:1(6Z))	SLM:000399780	SLM:000393288	SLM:000001201 (n-acyl)	CCCCCCCCCCCCCCC[C@@H](O)[C@H](CO[C@@H]1O[C@H](CO)[C@@H](O[C@@H]2O[C@H](CO)[C@H](O)[C@H](O)[C@H]2O)[C@H](O)[C@H]1O)NC(=O)CCCC\C=C/CCCCCCCCCCC	InChI=1S/C48H91NO13/c1-3-5-7-9-11-13-15-17-18-20-22-24-26-28-30-32-40(53)49-36(37(52)31-29-27-25-23-21-19-16-14-12-10-8-6-4-2)35-59-47-45(58)43(56)46(39(34-51)61-47)62-48-44(57)42(55)41(54)38(33-50)60-48/h22,24,36-39,41-48,50-52,54-58H,3-21,23,25-35H2,1-2H3,(H,49,53)/b24-22-/t36-,37+,38+,39+,41-,42-,43+,44+,45+,46+,47+,48-/m0/s1	InChIKey=VNUWLKFDJMGAGI-FRYZSOPTSA-N	C48H91NO13	0	890.235000	889.649042	889.648493	890.656318	928.612200	912.638263	896.664497	907.682868	888.641766	924.618443	948.662895
"""  # noqa: E501
