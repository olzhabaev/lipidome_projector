"""Module concerning the matching of lipid datasets."""

import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Self, TextIO

import pandas as pd

from lipid_data_processing.notation.parsing import ParsedDataset


logger: logging.Logger = logging.getLogger(__name__)


_DEFAULT_SYNONYMS: dict[str, list[str]] = {
    "HexCer": ["GlcCer", "GalCer"],
}


@dataclass(frozen=True)
class _ValidationMixin:
    @classmethod
    def _chk_input(cls, df: pd.DataFrame, col_names: list[str]) -> None:
        cls._chk_missing_columns(df, col_names)
        cls._chk_erroneous_columns(df, col_names)
        cls._chk_nan_values(df)

    @staticmethod
    def _chk_missing_columns(df: pd.DataFrame, col_names: list[str]) -> None:
        missing_col_names: list[str] = [
            col_name for col_name in col_names if col_name not in df.columns
        ]
        if missing_col_names:
            raise ValueError(
                f"Missing columns in dataframe: {', '.join(missing_col_names)}"
            )

    @staticmethod
    def _chk_erroneous_columns(df: pd.DataFrame, col_names: list[str]) -> None:
        erroneous_col_names: list[str] = [
            col_name for col_name in df.columns if col_name not in col_names
        ]
        if erroneous_col_names:
            raise ValueError(
                "Erroneous columns in "
                f"dataframe: {', '.join(erroneous_col_names)}"
            )

    @staticmethod
    def _chk_nan_values(df: pd.DataFrame) -> None:
        if df.isnull().values.any():
            raise ValueError("Dataframe contains NaN values.")


@dataclass(frozen=True)
class MatchesInfo(_ValidationMixin):
    dataframe: pd.DataFrame
    to_match_index_col_name: str
    match_to_index_col_name: str
    to_match_parsed_name_col_name: str
    to_match_original_name_col_name: str
    match_to_parsed_name_col_name: str
    match_to_original_name_col_name: str

    def __post_init__(self) -> None:
        self._chk_input(
            self.dataframe,
            [
                self.to_match_index_col_name,
                self.match_to_index_col_name,
                self.to_match_parsed_name_col_name,
                self.to_match_original_name_col_name,
                self.match_to_parsed_name_col_name,
                self.match_to_original_name_col_name,
            ],
        )


@dataclass(frozen=True)
class Names(_ValidationMixin):
    dataframe: pd.DataFrame
    parsed_name_col_name: str
    original_name_col_name: str

    def __post_init__(self) -> None:
        self._chk_input(
            self.dataframe,
            [self.parsed_name_col_name, self.original_name_col_name],
        )


@dataclass(frozen=True)
class FilteredLipids(_ValidationMixin):
    dataframe: pd.DataFrame
    parsed_name_col_name: str
    original_name_col_name: str
    fa_violations_col_name: str
    lcb_violations_col_name: str

    def __post_init__(self) -> None:
        self._chk_input(
            self.dataframe,
            [
                self.parsed_name_col_name,
                self.original_name_col_name,
                self.fa_violations_col_name,
                self.lcb_violations_col_name,
            ],
        )


@dataclass(frozen=True)
class UnfilteredMatchingResults:
    matches_info: MatchesInfo
    parsed_no_match: Names
    original_name_no_match: Names


@dataclass(frozen=True)
class FilteringResults:
    constrained_matches_info: MatchesInfo
    filtered_lipids: FilteredLipids


@dataclass(frozen=True)
class MatchingResults(UnfilteredMatchingResults, FilteringResults):
    @classmethod
    def from_constituents(
        cls,
        unfiltered_matching_results: UnfilteredMatchingResults,
        filtering_results: FilteringResults,
    ) -> Self:
        return cls(
            matches_info=unfiltered_matching_results.matches_info,
            parsed_no_match=unfiltered_matching_results.parsed_no_match,
            original_name_no_match=unfiltered_matching_results.original_name_no_match,  # noqa: E501
            constrained_matches_info=filtering_results.constrained_matches_info,  # noqa: E501
            filtered_lipids=filtering_results.filtered_lipids,
        )


@dataclass(frozen=True)
class MatchIndexPairs(_ValidationMixin):
    dataframe: pd.DataFrame
    to_match_col_name: str
    match_to_col_name: str

    @property
    def to_match_index(self) -> pd.Index:
        return pd.Index(self.dataframe[self.to_match_col_name])

    @property
    def match_to_index(self) -> pd.Index:
        return pd.Index(self.dataframe[self.match_to_col_name])

    def __post_init__(self) -> None:
        self._chk_input(
            self.dataframe, [self.to_match_col_name, self.match_to_col_name]
        )


@dataclass(frozen=True)
class ConstraintsDataset:
    fa_constraints: pd.Series
    lcb_constraints: pd.Series

    def __post_init__(self) -> None:
        self._chk_input(self.fa_constraints, self.lcb_constraints)

    @classmethod
    def from_constraint_csv_input(
        cls,
        fa_constraints_csv_input: Path | TextIO,
        lcb_constraints_csv_input: Path | TextIO,
    ) -> Self:
        """Read constraints dataset from csv input.
        :param fa_constraints_csv_input:  FA constraints csv input.
        :param lcb_constraints_csv_input: LCB constraints csv input.
        :param parse_constraints: Whether to parse constraints.
        :return: ConstraintsDataset object.
        """
        if isinstance(fa_constraints_csv_input, Path):
            logger.info(
                f"Read FA constraints from: {fa_constraints_csv_input}"
            )
        else:
            logger.info("Read FA constraints from file-like object.")

        fa_constraints_df: pd.DataFrame = pd.read_csv(
            fa_constraints_csv_input, sep="\t", header=None
        )

        fa_constraints: pd.Series = fa_constraints_df[
            fa_constraints_df.columns[0]
        ]

        fa_constraints.name = "FA"

        if isinstance(lcb_constraints_csv_input, Path):
            logger.info(
                f"Read LCB constraints from: {lcb_constraints_csv_input}"
            )
        else:
            logger.info("Read LCB constraints from file-like object.")

        lcb_constraints_df: pd.DataFrame = pd.read_csv(
            lcb_constraints_csv_input, sep="\t", header=None
        )

        lcb_constraints: pd.Series = lcb_constraints_df[
            lcb_constraints_df.columns[0]
        ]

        lcb_constraints.name = "LCB"

        constraints_ds: Self = cls(
            fa_constraints=fa_constraints,
            lcb_constraints=lcb_constraints,
        )

        return constraints_ds

    def _chk_input(
        self, fa_constraints: pd.Series, lcb_constraints: pd.Series
    ) -> None:
        if len(fa_constraints) == 0:
            raise ValueError("FA constraints series empty.")

        if len(lcb_constraints) == 0:
            raise ValueError("LCB constraints series empty.")


def perform_constrained_match(
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    constraints_ds: ConstraintsDataset,
    class_synonyms: dict[str, list[str]] | None = None,
) -> MatchingResults:
    """Perform a constrained match between two datasets.
    :param to_match_ds: Dataset to match.
    :param match_to_ds: Dataset to match to.
    :param constraints_ds: Constraints dataset.
    :param duplicate_removal_feature: Feature to use for
        duplicate removal.
    :return: Matching results.
    """
    match_index_pairs: MatchIndexPairs = _match_cases(
        to_match_ds=to_match_ds,
        match_to_ds=match_to_ds,
        class_synonyms=class_synonyms,
    )

    unfiltered_matching_results: UnfilteredMatchingResults = (
        _compile_unfiltered_matching_results(
            match_index_pairs, to_match_ds, match_to_ds
        )
    )

    filtering_results: FilteringResults = _filter_matches(
        match_index_pairs=match_index_pairs,
        matches_info=unfiltered_matching_results.matches_info,
        to_match_ds=to_match_ds,
        match_to_ds=match_to_ds,
        constraints_ds=constraints_ds,
    )

    return MatchingResults.from_constituents(
        unfiltered_matching_results, filtering_results
    )


def _match_cases(
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    to_match_col_name: str = "TO_MATCH_INDEX",
    match_to_col_name: str = "MATCH_TO_INDEX",
    class_synonyms: dict[str, list[str]] | None = None,
) -> MatchIndexPairs:
    generic_match_index_pairs: MatchIndexPairs = _match_by_parsed_name(
        to_match_ds=to_match_ds,
        match_to_ds=match_to_ds,
        to_match_col_name=to_match_col_name,
        match_to_col_name=match_to_col_name,
    )

    class_synonyms = _proc_class_synonyms(class_synonyms)

    synonym_match_index_pairs: MatchIndexPairs = (
        _match_by_parsed_name_with_synonyms(
            to_match_ds=to_match_ds,
            match_to_ds=match_to_ds,
            to_match_col_name=to_match_col_name,
            match_to_col_name=match_to_col_name,
            class_synonyms=class_synonyms,
        )
    )

    original_name_match_index_pairs: MatchIndexPairs = _match_by_original_name(
        to_match_ds=to_match_ds,
        match_to_ds=match_to_ds,
        to_match_col_name=to_match_col_name,
        match_to_col_name=match_to_col_name,
    )

    all_match_index_pairs: MatchIndexPairs = _combine_case_matches(
        generic_match_index_pairs,
        synonym_match_index_pairs,
        original_name_match_index_pairs,
    )

    return all_match_index_pairs


def _compile_unfiltered_matching_results(
    match_index_pairs: MatchIndexPairs,
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
) -> UnfilteredMatchingResults:
    matches_info_df: MatchesInfo = _gen_matches_info(
        match_index_pairs, to_match_ds, match_to_ds
    )

    parsed_no_match: Names = _get_parsed_no_match_lipids(
        match_index_pairs, to_match_ds
    )

    original_name_no_match: Names = _get_original_name_no_match_lipids(
        match_index_pairs, to_match_ds
    )

    return UnfilteredMatchingResults(
        matches_info=matches_info_df,
        parsed_no_match=parsed_no_match,
        original_name_no_match=original_name_no_match,
    )


def _gen_matches_info(
    match_index_pairs: MatchIndexPairs,
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    to_match_prefix: str = "TO_MATCH_",
    match_to_prefix: str = "MATCH_TO_",
) -> MatchesInfo:
    matches_info_df: pd.DataFrame = (
        match_index_pairs.dataframe.merge(
            to_match_ds.name_df.add_prefix(to_match_prefix),
            how="left",
            left_on=match_index_pairs.to_match_col_name,
            right_index=True,
        )
        .merge(
            match_to_ds.name_df.add_prefix(match_to_prefix),
            how="left",
            left_on=match_index_pairs.match_to_col_name,
            right_index=True,
        )
        .reset_index(drop=True)
    )

    to_match_original_name = (
        f"{to_match_prefix}{to_match_ds.col_names.original_name}"
    )
    to_match_parsed_name = (
        f"{to_match_prefix}{to_match_ds.col_names.parsed_name}"
    )
    match_to_original_name = (
        f"{match_to_prefix}{match_to_ds.col_names.original_name}"
    )
    match_to_parsed_name = (
        f"{match_to_prefix}{match_to_ds.col_names.parsed_name}"
    )

    return MatchesInfo(
        dataframe=matches_info_df,
        to_match_index_col_name=match_index_pairs.to_match_col_name,
        match_to_index_col_name=match_index_pairs.match_to_col_name,
        to_match_original_name_col_name=to_match_original_name,
        to_match_parsed_name_col_name=to_match_parsed_name,
        match_to_original_name_col_name=match_to_original_name,
        match_to_parsed_name_col_name=match_to_parsed_name,
    )


def _get_parsed_no_match_lipids(
    match_index_pairs: MatchIndexPairs, to_match_ds: ParsedDataset
) -> Names:
    parsed_no_match: pd.DataFrame = to_match_ds.name_df.loc[
        (to_match_ds.parsed_names != "")
        & ~(to_match_ds.name_df.index.isin(match_index_pairs.to_match_index))
    ].reset_index(drop=True)

    return Names(
        dataframe=parsed_no_match,
        parsed_name_col_name=to_match_ds.col_names.parsed_name,
        original_name_col_name=to_match_ds.col_names.original_name,
    )


# TODO Make clear, that these results only contain
# original name no match lipids, which were not parsed
# in the first place.
def _get_original_name_no_match_lipids(
    match_index_pairs: MatchIndexPairs, to_match_ds: ParsedDataset
) -> Names:
    original_name_no_match: pd.DataFrame = to_match_ds.name_df[
        (to_match_ds.parsed_names == "")
        & ~(to_match_ds.name_df.index.isin(match_index_pairs.to_match_index))
    ].reset_index(drop=True)

    return Names(
        dataframe=original_name_no_match,
        parsed_name_col_name=to_match_ds.col_names.parsed_name,
        original_name_col_name=to_match_ds.col_names.original_name,
    )


def _proc_class_synonyms(
    class_synonyms: dict[str, list[str]] | None,
) -> dict[str, list[str]]:
    return _DEFAULT_SYNONYMS | (
        class_synonyms if class_synonyms is not None else {}
    )


def _combine_case_matches(
    generic_match_index_pairs: MatchIndexPairs,
    synonym_match_index_pairs: MatchIndexPairs,
    original_name_match_index_pairs: MatchIndexPairs,
) -> MatchIndexPairs:
    all_match_index_pairs: pd.DataFrame = pd.concat(
        (
            df
            for df in (
                generic_match_index_pairs.dataframe,
                synonym_match_index_pairs.dataframe,
                original_name_match_index_pairs.dataframe,
            )
            if not df.empty
        ),
        ignore_index=True,
    ).drop_duplicates()

    return MatchIndexPairs(
        all_match_index_pairs,
        generic_match_index_pairs.to_match_col_name,
        generic_match_index_pairs.match_to_col_name,
    )


def _match_by_original_name(
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    to_match_col_name: str,
    match_to_col_name: str,
) -> MatchIndexPairs:
    to_match_name_index_df: pd.DataFrame = (
        to_match_ds.original_names.rename_axis(to_match_col_name).reset_index()
    )

    match_to_name_index_df: pd.DataFrame = (
        match_to_ds.original_names.rename_axis(match_to_col_name).reset_index()
    )

    match_index_pairs_df: pd.DataFrame = (
        to_match_name_index_df.merge(
            match_to_name_index_df,
            how="left",
            left_on=to_match_ds.col_names.original_name,
            right_on=match_to_ds.col_names.original_name,
            validate="one_to_many",
        )
        .drop(
            columns=[
                to_match_ds.col_names.original_name,
                match_to_ds.col_names.original_name,
            ]
        )
        .dropna()
    )

    return MatchIndexPairs(
        match_index_pairs_df, to_match_col_name, match_to_col_name
    )


def _match_by_parsed_name(
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    to_match_col_name: str,
    match_to_col_name: str,
) -> MatchIndexPairs:
    matched_groups: list[pd.DataFrame] = [
        group.rename_axis(index=to_match_col_name)
        .reset_index()
        .merge(
            match_to_ds.classification_df.rename_axis(
                index=match_to_col_name
            ).reset_index(),
            how="left",
            left_on=to_match_ds.col_names.parsed_name,
            right_on=str(level),
        )[[to_match_col_name, match_to_col_name]]
        .dropna()
        for level, group in to_match_ds.name_level_df.groupby(
            to_match_ds.col_names.level
        )
        if level in match_to_ds.classification_df.columns
    ]

    match_index_pairs_df: pd.DataFrame = (
        pd.concat(matched_groups, ignore_index=True)
        if matched_groups
        else pd.DataFrame(columns=[to_match_col_name, match_to_col_name])
    )

    return MatchIndexPairs(
        match_index_pairs_df, to_match_col_name, match_to_col_name
    )


def _match_by_parsed_name_with_synonyms(
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    to_match_col_name: str,
    match_to_col_name: str,
    class_synonyms: dict[str, list[str]],
) -> MatchIndexPairs:
    synonym_match_index_pair_dfs: list[pd.DataFrame] = [
        _replace_class_with_synonym_and_match(
            to_match_ds=to_match_ds,
            match_to_ds=match_to_ds,
            to_match_col_name=to_match_col_name,
            match_to_col_name=match_to_col_name,
            lipid_class=lipid_class,
            synonym=synonym,
        )
        for lipid_class, synonyms in class_synonyms.items()
        if _chk_class_exists(to_match_ds, lipid_class)
        for synonym in synonyms
    ]

    match_index_pair_df: pd.DataFrame = (
        pd.concat(synonym_match_index_pair_dfs).drop_duplicates()
        if synonym_match_index_pair_dfs
        else pd.DataFrame(columns=[to_match_col_name, match_to_col_name])
    )

    return MatchIndexPairs(
        match_index_pair_df, to_match_col_name, match_to_col_name
    )


def _chk_class_exists(to_match_ds: ParsedDataset, lipid_class: str) -> bool:
    class_name_level_df: pd.DataFrame = to_match_ds.name_level_df[
        to_match_ds.name_level_df[
            to_match_ds.col_names.parsed_name
        ].str.startswith(lipid_class)
    ]

    return len(class_name_level_df) != 0


def _replace_class_with_synonym_and_match(
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    to_match_col_name: str,
    match_to_col_name: str,
    lipid_class: str,
    synonym: str,
) -> pd.DataFrame:
    renamed_df: pd.DataFrame = to_match_ds.df.copy()

    renamed_df[to_match_ds.col_names.parsed_name] = (
        to_match_ds.parsed_names.str.replace(lipid_class, synonym)
    )

    renamed_ds: ParsedDataset = ParsedDataset(
        df=renamed_df,
        col_names=to_match_ds.col_names,
    )

    match_index_pairs_df: pd.DataFrame = _match_by_parsed_name(
        renamed_ds, match_to_ds, to_match_col_name, match_to_col_name
    ).dataframe

    return match_index_pairs_df


def _filter_matches(
    match_index_pairs: MatchIndexPairs,
    matches_info: MatchesInfo,
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    constraints_ds: ConstraintsDataset,
) -> FilteringResults:
    fa_constraint_masks: pd.DataFrame = _get_fa_constraint_masks(
        match_index_pairs.match_to_index,
        match_to_ds,
        constraints_ds.fa_constraints,
    )

    fa_constraint_filter: pd.Series = fa_constraint_masks.all(axis="columns")

    lcb_constraint_filter: pd.Series = _get_lcb_constraint_filter(
        match_index_pairs.match_to_index,
        match_to_ds,
        constraints_ds.lcb_constraints,
    )

    component_filter: pd.Series = fa_constraint_filter & lcb_constraint_filter

    constrained_matches_info: MatchesInfo = _get_constrained_matches_info(
        matches_info, component_filter
    )

    filtered_lipids: FilteredLipids = _get_filtered_lipids(
        match_index_pairs=match_index_pairs,
        to_match_ds=to_match_ds,
        match_to_ds=match_to_ds,
        fa_constraint_masks=fa_constraint_masks,
        lcb_constraint_filter=lcb_constraint_filter,
        component_filter=component_filter,
    )

    return FilteringResults(constrained_matches_info, filtered_lipids)


def _get_constrained_matches_info(
    matches_info: MatchesInfo, component_filter: pd.Series
) -> MatchesInfo:
    if matches_info.dataframe.empty:
        return matches_info

    constrained_matches_info_df: pd.DataFrame = matches_info.dataframe.loc[
        component_filter.to_numpy(), :
    ].reset_index(drop=True)

    return MatchesInfo(
        dataframe=constrained_matches_info_df,
        to_match_index_col_name=matches_info.to_match_index_col_name,
        match_to_index_col_name=matches_info.match_to_index_col_name,
        to_match_parsed_name_col_name=matches_info.to_match_parsed_name_col_name,  # noqa: E501
        to_match_original_name_col_name=matches_info.to_match_original_name_col_name,  # noqa: E501
        match_to_parsed_name_col_name=matches_info.match_to_parsed_name_col_name,  # noqa: E501
        match_to_original_name_col_name=matches_info.match_to_original_name_col_name,  # noqa: E501
    )


def _get_filtered_lipids(
    match_index_pairs: MatchIndexPairs,
    to_match_ds: ParsedDataset,
    match_to_ds: ParsedDataset,
    fa_constraint_masks: pd.DataFrame,
    lcb_constraint_filter: pd.Series,
    component_filter: pd.Series,
) -> FilteredLipids:
    fa_violations_col_name: str = "FA_VIOLATIONS"
    lcb_violations_col_name: str = "LCB_VIOLATIONS"

    if match_index_pairs.dataframe.empty:
        return _gen_empty_filtered_lipids(
            to_match_ds.col_names.parsed_name,
            to_match_ds.col_names.original_name,
            fa_violations_col_name,
            lcb_violations_col_name,
        )

    passed_col_name: str = "PASSED"

    fa_violations: pd.DataFrame = _get_fa_violations(
        match_index_pairs, match_to_ds, fa_constraint_masks
    )

    lcb_violations: pd.Series = _get_lcb_violations(
        match_index_pairs, match_to_ds, lcb_constraint_filter
    )

    index_component_filter_df: pd.DataFrame = (
        match_index_pairs.dataframe.merge(
            component_filter.rename(passed_col_name),
            how="left",
            left_on=match_index_pairs.match_to_col_name,
            right_index=True,
        )
        .merge(
            to_match_ds.name_df,
            how="left",
            left_on=match_index_pairs.to_match_col_name,
            right_index=True,
        )
        .merge(
            fa_violations,
            how="left",
            left_on=match_index_pairs.match_to_col_name,
            right_index=True,
        )
        .merge(
            lcb_violations,
            how="left",
            left_on=match_index_pairs.match_to_col_name,
            right_index=True,
        )
    )

    filtered_lipids_df: pd.DataFrame = (
        index_component_filter_df.groupby(match_index_pairs.to_match_col_name)
        .apply(
            lambda group: _proc_filter_group(
                group,
                passed_col_name,
                match_to_ds,
                fa_violations_col_name,
                lcb_violations_col_name,
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    if filtered_lipids_df.empty:
        return _gen_empty_filtered_lipids(
            to_match_ds.col_names.parsed_name,
            to_match_ds.col_names.original_name,
            fa_violations_col_name,
            lcb_violations_col_name,
        )

    return FilteredLipids(
        dataframe=filtered_lipids_df,
        parsed_name_col_name=to_match_ds.col_names.parsed_name,
        original_name_col_name=to_match_ds.col_names.original_name,
        fa_violations_col_name=fa_violations_col_name,
        lcb_violations_col_name=lcb_violations_col_name,
    )


def _gen_empty_filtered_lipids(
    parsed_name_col_name: str,
    original_name_col_name: str,
    fa_violations_col_name: str,
    lcb_violations_col_name: str,
) -> FilteredLipids:
    return FilteredLipids(
        dataframe=pd.DataFrame(
            columns=[
                parsed_name_col_name,
                original_name_col_name,
                fa_violations_col_name,
                lcb_violations_col_name,
            ]
        ),
        parsed_name_col_name=parsed_name_col_name,
        original_name_col_name=original_name_col_name,
        fa_violations_col_name=fa_violations_col_name,
        lcb_violations_col_name=lcb_violations_col_name,
    )


def _proc_filter_group(
    group: pd.DataFrame,
    passed_col_name: str,
    match_to_ds: ParsedDataset,
    fa_violations_col_name: str,
    lcb_violations_col_name: str,
) -> pd.DataFrame:
    if group[passed_col_name].any():
        return pd.DataFrame()

    fa_violations: list[str] = (
        pd.Series(pd.unique(group[match_to_ds.col_names.fas].values.ravel()))
        .dropna()
        .tolist()
    )

    lcb_violations: list[str] = (
        pd.Series(group[match_to_ds.col_names.lcb].unique()).dropna().tolist()
    )

    filtered_group: pd.DataFrame = (
        pd.Series(
            {
                match_to_ds.col_names.parsed_name: group[
                    match_to_ds.col_names.parsed_name
                ].iloc[0],
                match_to_ds.col_names.original_name: group[
                    match_to_ds.col_names.original_name
                ].iloc[0],
                fa_violations_col_name: fa_violations,
                lcb_violations_col_name: lcb_violations,
            }
        )
        .to_frame()
        .T
    )

    return filtered_group


def _get_fa_violations(
    match_index_pairs: MatchIndexPairs,
    match_to_ds: ParsedDataset,
    fa_constraint_masks: pd.DataFrame,
) -> pd.DataFrame:
    fa_violations: pd.DataFrame = match_to_ds.fas.loc[
        match_index_pairs.match_to_index
    ][~fa_constraint_masks].dropna(how="all")

    return fa_violations


def _get_lcb_violations(
    match_index_pairs: MatchIndexPairs,
    match_to_ds: ParsedDataset,
    lcb_constraint_filter: pd.Series,
) -> pd.Series:
    lcb_violations: pd.Series = match_to_ds.lcb[
        match_index_pairs.match_to_index
    ][~lcb_constraint_filter]

    return lcb_violations


def _get_lcb_constraint_filter(
    matches_index: pd.Index,
    match_to_ds: ParsedDataset,
    lcb_constraints: pd.Series,
) -> pd.Series:
    matches_lcbs: pd.Series = match_to_ds.lcb.loc[matches_index]

    empty_lcbs: pd.Series = matches_lcbs.str.fullmatch("")

    na_lcbs: pd.Series = matches_lcbs.str.fullmatch("N/A")

    lcb_in_constraints: pd.Series = matches_lcbs.isin(lcb_constraints)

    lcb_constraint_filter: pd.Series = (
        empty_lcbs | na_lcbs | lcb_in_constraints
    )

    return lcb_constraint_filter


def _get_fa_constraint_masks(
    matches_index: pd.Index,
    match_to_ds: ParsedDataset,
    fa_constraints: pd.Series,
) -> pd.DataFrame:
    fas: pd.DataFrame = match_to_ds.fas.loc[matches_index]

    fa_constraint_masks: pd.DataFrame = fas.apply(
        lambda column: _mark_fa_constraint_violations(column, fa_constraints),
        axis="index",
    )

    return fa_constraint_masks


def _mark_fa_constraint_violations(
    fas: pd.Series, fa_constraints: pd.Series
) -> pd.Series:
    processed_fas: pd.Series = _remove_hydroxylations(
        _remove_fa_bond_alterations(fas)
    )

    empty_fas: pd.Series = processed_fas.str.fullmatch("")

    na_fas: pd.Series = processed_fas.str.fullmatch("N/A")

    zero_fas: pd.Series = processed_fas.str.fullmatch("0:0")

    fa_in_constraints: pd.Series = processed_fas.isin(fa_constraints)

    fa_constraint_mask: pd.Series = (
        empty_fas | na_fas | zero_fas | fa_in_constraints
    )

    return fa_constraint_mask


def _remove_hydroxylations(names: pd.Series) -> pd.Series:
    return names.str.replace(";[0-9]+OH", "", regex=True)


def _remove_fa_bond_alterations(names: pd.Series) -> pd.Series:
    """Remove FA bond alterations (O-/ P-) from names.
    :param names: Series of lipid names.
    :return: Series of lipid names with FA bond alterations removed.
    """

    return names.str.replace("[OP]-", "", regex=True)
