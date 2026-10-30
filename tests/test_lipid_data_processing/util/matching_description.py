"""Module concerning the description of lipidomes."""

import logging

from dataclasses import dataclass

import pandas as pd

from tests.test_lipid_data_processing.util.lipid_description import (
    LipidCollection,
    LipidDescription,
    ParsedLipid,
)

from lipid_data_processing.notation.matching import (
    ConstraintsDataset,
    FilteredLipids,
    MatchesInfo,
    MatchingResults,
    Names,
    perform_constrained_match,
)
from lipid_data_processing.notation.parsing import ParsedDataset

logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MatchingCase:
    match_to_ds: ParsedDataset
    to_match_ds: ParsedDataset
    constraints_ds: ConstraintsDataset
    target_matching_results: MatchingResults
    test_matching_results: MatchingResults


class LipidIsomersPairs:
    def __init__(
        self,
        lipid_isomers_pairs: list[
            tuple[LipidDescription, list[LipidDescription]]
        ],
    ):
        self._lipid_isomers_pairs = lipid_isomers_pairs

    def get_lipid_descriptions(self) -> list[LipidDescription]:
        return [
            lipid_isomer_pair[0]
            for lipid_isomer_pair in self._lipid_isomers_pairs
        ]

    def get_isomer_descriptions(self) -> list[LipidDescription]:
        return [
            isomer
            for lipid_isomer_pair in self._lipid_isomers_pairs
            for isomer in lipid_isomer_pair[1]
        ]

    def get_lipid_collection(self) -> LipidCollection:
        return LipidCollection(self.get_lipid_descriptions())

    def get_isomer_collection(self) -> LipidCollection:
        return LipidCollection(self.get_isomer_descriptions())

    def to_lipid_parsed_df(self) -> pd.DataFrame:
        return self.get_lipid_collection().to_parsed_df()

    def to_lipid_name_df(self) -> pd.DataFrame:
        return self.get_lipid_collection().to_name_df()

    def to_matches_info_df(self) -> pd.DataFrame:
        matches_info_df: pd.DataFrame = pd.DataFrame(
            [
                {
                    "TO_MATCH_INDEX": lipid_isomers_pair[0].index,
                    "MATCH_TO_INDEX": isomer.index,
                    "TO_MATCH_"
                    + ParsedLipid.parsed_name_col_name: lipid_isomers_pair[
                        0
                    ].parsed_lipid.parsed_name,
                    "TO_MATCH_"
                    + ParsedLipid.original_name_col_name: lipid_isomers_pair[
                        0
                    ].original_name,
                    "MATCH_TO_PARSED_NAME": isomer.parsed_lipid.parsed_name,
                    "MATCH_TO_ORIGINAL_NAME": isomer.original_name,
                }
                for lipid_isomers_pair in self._lipid_isomers_pairs
                for isomer in lipid_isomers_pair[1]
            ],
            dtype="string",
        )

        return matches_info_df

    def get_pairs_list_fa_constraints(self) -> pd.Series:
        fa_constraints: pd.Series = pd.concat(
            [
                self._get_lipid_fas(isomer)
                for isomer in self.get_isomer_descriptions()
            ]
        ).drop_duplicates()

        fa_constraints = fa_constraints[
            ~fa_constraints.isin(["", "N/A", "MISSING"])
        ]

        return fa_constraints

    def get_pairs_list_lcb_constraints(self) -> pd.Series:
        lcb_constraints: pd.Series = pd.Series(
            [
                self._get_lipid_lcb(isomer)
                for isomer in self.get_isomer_descriptions()
            ]
        ).drop_duplicates()

        lcb_constraints = lcb_constraints[
            ~lcb_constraints.isin(["", "N/A", "MISSING"])
        ]

        return lcb_constraints

    @staticmethod
    def _get_lipid_fas(lipid: LipidDescription) -> pd.Series:
        fa_constraints: pd.Series = pd.Series(
            [
                lipid.parsed_lipid.fa1,
                lipid.parsed_lipid.fa2,
                lipid.parsed_lipid.fa3,
                lipid.parsed_lipid.fa4,
            ]
        )

        fa_constraints = fa_constraints[fa_constraints != ""]

        return fa_constraints

    @staticmethod
    def _get_lipid_lcb(lipid: LipidDescription) -> str:
        return lipid.parsed_lipid.lcb


class FilteredLipidsCollection:
    def __init__(
        self,
        lipid_constraints_pairs: list[
            tuple[LipidDescription, list[str], list[str]]
        ],
    ):
        self._lipid_constraints_pairs: list[
            tuple[LipidDescription, list[str], list[str]]
        ] = lipid_constraints_pairs

    def to_df(self) -> pd.DataFrame:
        filtered_lipids_df: pd.DataFrame = pd.DataFrame(
            [
                {
                    ParsedLipid.parsed_name_col_name: lipid_constraints_pair[
                        0
                    ].parsed_lipid.parsed_name,
                    ParsedLipid.original_name_col_name: lipid_constraints_pair[  # noqa: E501
                        0
                    ].original_name,
                    "FA_VIOLATIONS": lipid_constraints_pair[1],
                    "LCB_VIOLATIONS": lipid_constraints_pair[2],
                }
                for lipid_constraints_pair in self._lipid_constraints_pairs
            ],
        )

        return filtered_lipids_df


def lipid_isomers_pairs_to_lipidome_matching_test_data(
    lipid_isomers_pairs: LipidIsomersPairs,
    constrained_lipid_isomers_pairs: LipidIsomersPairs,
    filtered_lipids_collection: FilteredLipidsCollection,
    parsed_no_match_lipids: LipidCollection,
    original_name_no_match_lipids: LipidCollection,
    match_to_ds: ParsedDataset,
) -> MatchingCase:

    fa_constraints: pd.Series = (
        constrained_lipid_isomers_pairs.get_pairs_list_fa_constraints()
    )

    lcb_constraints: pd.Series = (
        constrained_lipid_isomers_pairs.get_pairs_list_lcb_constraints()
    )

    parsed_lipids_df: pd.DataFrame = pd.concat(
        [
            lipid_isomers_pairs.to_lipid_parsed_df(),
            parsed_no_match_lipids.to_parsed_df(),
            original_name_no_match_lipids.to_parsed_df(),
        ],
    )

    matches_info_df: pd.DataFrame = lipid_isomers_pairs.to_matches_info_df()

    constrained_matches_df: pd.DataFrame = (
        constrained_lipid_isomers_pairs.to_matches_info_df()
    )

    filtered_lipids_df: pd.DataFrame = filtered_lipids_collection.to_df()

    parsed_no_match_df: pd.DataFrame = (
        parsed_no_match_lipids.to_name_df().reset_index(drop=True)
    )

    original_name_no_match_df: pd.DataFrame = (
        original_name_no_match_lipids.to_name_df().reset_index(drop=True)
    )

    test_matching_results: MatchingResults = perform_constrained_match(
        to_match_ds=ParsedDataset(parsed_lipids_df),
        match_to_ds=match_to_ds,
        constraints_ds=ConstraintsDataset(fa_constraints, lcb_constraints),
    )

    matches_info: MatchesInfo = MatchesInfo(
        dataframe=matches_info_df,
        to_match_index_col_name="TO_MATCH_INDEX",
        match_to_index_col_name="MATCH_TO_INDEX",
        to_match_parsed_name_col_name="TO_MATCH_PARSED_NAME",
        to_match_original_name_col_name="TO_MATCH_ORIGINAL_NAME",
        match_to_parsed_name_col_name="MATCH_TO_PARSED_NAME",
        match_to_original_name_col_name="MATCH_TO_ORIGINAL_NAME",
    )

    constrained_matches_info: MatchesInfo = MatchesInfo(
        dataframe=constrained_matches_df,
        to_match_index_col_name="TO_MATCH_INDEX",
        match_to_index_col_name="MATCH_TO_INDEX",
        to_match_parsed_name_col_name="TO_MATCH_PARSED_NAME",
        to_match_original_name_col_name="TO_MATCH_ORIGINAL_NAME",
        match_to_parsed_name_col_name="MATCH_TO_PARSED_NAME",
        match_to_original_name_col_name="MATCH_TO_ORIGINAL_NAME",
    )

    parsed_no_match: Names = Names(
        dataframe=parsed_no_match_df,
        parsed_name_col_name="PARSED_NAME",
        original_name_col_name="ORIGINAL_NAME",
    )

    original_name_no_match: Names = Names(
        dataframe=original_name_no_match_df,
        parsed_name_col_name="PARSED_NAME",
        original_name_col_name="ORIGINAL_NAME",
    )

    filtered_lipids: FilteredLipids = FilteredLipids(
        dataframe=filtered_lipids_df,
        parsed_name_col_name="PARSED_NAME",
        original_name_col_name="ORIGINAL_NAME",
        fa_violations_col_name="FA_VIOLATIONS",
        lcb_violations_col_name="LCB_VIOLATIONS",
    )

    matching_case: MatchingCase = MatchingCase(
        match_to_ds=match_to_ds,
        to_match_ds=ParsedDataset(parsed_lipids_df),
        constraints_ds=ConstraintsDataset(fa_constraints, lcb_constraints),
        target_matching_results=MatchingResults(
            matches_info=matches_info,
            constrained_matches_info=constrained_matches_info,
            parsed_no_match=parsed_no_match,
            original_name_no_match=original_name_no_match,
            filtered_lipids=filtered_lipids,
        ),
        test_matching_results=test_matching_results,
    )

    return matching_case
