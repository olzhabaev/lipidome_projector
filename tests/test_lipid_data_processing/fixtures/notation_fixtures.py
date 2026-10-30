"""Module concerning lipidome fixtures."""

import logging

import pytest

import pandas as pd

from lipid_data_processing.notation.parsing import (
    ParsedDataset,
    ParsedDSColNames,
)

from tests.test_lipid_data_processing.fixtures.high_level_lipid_fixtures import *  # noqa: F401, F403, E501
from tests.test_lipid_data_processing.fixtures.lmsd_fixtures import *  # noqa: F401, F403, E501
from tests.test_lipid_data_processing.fixtures.misc_lipid_fixtures import *  # noqa: F401, F403, E501
from tests.test_lipid_data_processing.fixtures.sl_fixtures import *  # noqa: F401, F403, E501
from tests.test_lipid_data_processing.util.lipid_description import (
    LipidDescription,
    LipidCollection,
)
from tests.test_lipid_data_processing.util.matching_description import (
    FilteredLipidsCollection,
    LipidIsomersPairs,
    MatchingCase,
    lipid_isomers_pairs_to_lipidome_matching_test_data,
)

logger: logging.Logger = logging.getLogger(__name__)


# * MATCHING RESULTS ----------------------------------------------------------


@pytest.fixture(scope="session")
def parsed_lipid_feature_names() -> ParsedDSColNames:
    parsed_lipid_feature_names: ParsedDSColNames = ParsedDSColNames()

    return parsed_lipid_feature_names


@pytest.fixture(scope="session")
def parsing_relevant_col_names(
    parsed_lipid_feature_names: ParsedDSColNames,
) -> list[str]:
    relevant_col_names: list[str] = [
        parsed_lipid_feature_names.original_name,
        parsed_lipid_feature_names.parsed_name,
        parsed_lipid_feature_names.level,
        parsed_lipid_feature_names.category,
        parsed_lipid_feature_names.class_,
        parsed_lipid_feature_names.species,
        parsed_lipid_feature_names.molecular_species,
        parsed_lipid_feature_names.sn_position,
        parsed_lipid_feature_names.structure_defined,
        parsed_lipid_feature_names.full_structure,
        parsed_lipid_feature_names.complete_structure,
        parsed_lipid_feature_names.fa1,
        parsed_lipid_feature_names.fa2,
        parsed_lipid_feature_names.fa3,
        parsed_lipid_feature_names.fa4,
        parsed_lipid_feature_names.lcb,
    ]

    return relevant_col_names


@pytest.fixture(scope="session")
def match_to_ds(
    combined_db_parsed_df: pd.DataFrame,
    parsed_lipid_feature_names: ParsedDSColNames,
) -> ParsedDataset:
    match_to_ds: ParsedDataset = ParsedDataset(
        combined_db_parsed_df, parsed_lipid_feature_names
    )

    return match_to_ds


@pytest.fixture(scope="session")
def matching_case_1(
    dg_sp_24_0: LipidDescription,
    slm_000117321: LipidDescription,
    dg_sp_24_2: LipidDescription,
    dg_sp_32_0: LipidDescription,
    lmgl02010009: LipidDescription,
    dg_sp_32_1: LipidDescription,
    lmgl02010010: LipidDescription,
    tg_sp_54_3: LipidDescription,
    lmgl03010233: LipidDescription,
    lmgl03010237: LipidDescription,
    pc_sp_34_4: LipidDescription,
    slm_000012707: LipidDescription,
    slm_000012858: LipidDescription,
    cer_sp_34_1_2: LipidDescription,
    lmsp02010004: LipidDescription,
    lmsp02010036: LipidDescription,
    hex_cer_38_4_2: LipidDescription,
    slm_000395441: LipidDescription,
    slm_000395404: LipidDescription,
    teasterone: LipidDescription,
    lmst01030121: LipidDescription,
    unparseable_name_1: LipidDescription,
    match_to_ds: ParsedDataset,
) -> MatchingCase:

    lipid_isomers_pairs: LipidIsomersPairs = LipidIsomersPairs(
        [
            (dg_sp_24_0, [slm_000117321]),
            (dg_sp_32_0, [lmgl02010009]),
            (dg_sp_32_1, [lmgl02010010]),
            (tg_sp_54_3, [lmgl03010233, lmgl03010237]),
            (pc_sp_34_4, [slm_000012707, slm_000012858]),
            (cer_sp_34_1_2, [lmsp02010004, lmsp02010036]),
            (hex_cer_38_4_2, [slm_000395441, slm_000395404]),
            (teasterone, [lmst01030121]),
        ]
    )

    constrained_lipid_isomers_pairs: LipidIsomersPairs = LipidIsomersPairs(
        [
            (dg_sp_24_0, [slm_000117321]),
            (dg_sp_32_0, [lmgl02010009]),
            (tg_sp_54_3, [lmgl03010233]),
            (pc_sp_34_4, [slm_000012707]),
            (cer_sp_34_1_2, [lmsp02010004]),
            (hex_cer_38_4_2, [slm_000395441]),
            (teasterone, [lmst01030121]),
        ]
    )

    filtered_lipids: FilteredLipidsCollection = FilteredLipidsCollection(
        [(dg_sp_32_1, ["16:1(9Z)"], [])]
    )

    parsed_no_match_lipids: LipidCollection = LipidCollection(
        [
            dg_sp_24_2,
        ]
    )

    original_name_no_match_lipids: LipidCollection = LipidCollection(
        [
            unparseable_name_1,
        ]
    )

    matching_case: MatchingCase = (
        lipid_isomers_pairs_to_lipidome_matching_test_data(
            lipid_isomers_pairs=lipid_isomers_pairs,
            constrained_lipid_isomers_pairs=constrained_lipid_isomers_pairs,
            filtered_lipids_collection=filtered_lipids,
            parsed_no_match_lipids=parsed_no_match_lipids,
            original_name_no_match_lipids=original_name_no_match_lipids,
            match_to_ds=match_to_ds,
        )
    )

    return matching_case
