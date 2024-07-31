"""Module concerning the parsing of lipids with pygoslin."""

import logging

from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Self, TextIO

import pandas as pd

from pygoslin.domain.FattyAcid import FattyAcid
from pygoslin.domain.LipidAdduct import LipidAdduct
from pygoslin.domain.LipidCategory import LipidCategory
from pygoslin.domain.LipidLevel import LipidLevel
from pygoslin.parser.Parser import (
    GoslinParser,
    LipidMapsParser,
    LipidParser,
    SwissLipidsParser,
)

from tqdm import tqdm


logger: logging.Logger = logging.getLogger(__name__)


tqdm.pandas()


Parser = LipidParser | GoslinParser | LipidMapsParser | SwissLipidsParser


@dataclass(frozen=True)
class LipidParsingResults:
    original_name: str
    lipid: LipidAdduct | None
    status: str
    message: str


@dataclass(frozen=True)
class LipidParsingOutcomeTexts:
    success_label: str = "success"
    success_message: str = ""
    failure_label: str = "failed"
    failure_message_missing: str = "Missing name"
    failure_message_not_parsed: str = "Name can not be parsed"


@dataclass(frozen=True)
class ComponentMissingLabels:
    missing: str = "MISSING"
    not_applicable: str = "N/A"


@dataclass(frozen=True)
class ParsedLipidFeatureNames:
    original_name: str = "ORIGINAL_NAME"
    parsed_name: str = "PARSED_NAME"

    status: str = "STATUS"
    message: str = "MESSAGE"

    level: str = "LEVEL"

    category: str = "CATEGORY"
    class_: str = "CLASS"
    species: str = "SPECIES"
    molecular_species: str = "MOLECULAR_SPECIES"
    sn_position: str = "SN_POSITION"
    structure_defined: str = "STRUCTURE_DEFINED"
    full_structure: str = "FULL_STRUCTURE"
    complete_structure: str = "COMPLETE_STRUCTURE"

    fa1: str = "FA1"
    fa2: str = "FA2"
    fa3: str = "FA3"
    fa4: str = "FA4"

    lcb: str = "LCB"

    @property
    def col_names_list(self) -> list[str]:
        return list(getattr(self, field.name) for field in fields(self))

    @property
    def fas(self) -> list[str]:
        return [self.fa1, self.fa2, self.fa3, self.fa4]


@dataclass(frozen=True)
class ParsedDSColNames(ParsedLipidFeatureNames):
    index: str = "INDEX"


class ParsedDataset:
    def __init__(
        self,
        df: pd.DataFrame,
        col_names: ParsedDSColNames | None = None,
    ) -> None:
        """Initialise dataset.
        :param df: Dataset dataframe.
        :param col_names: Column names.
        """
        col_names = col_names if col_names is not None else ParsedDSColNames()

        self._validate_df(df, col_names)

        self._df: pd.DataFrame = df

        self._col_names: ParsedDSColNames = col_names

        self._success_df: pd.DataFrame = self._df.loc[
            (self._df[self._col_names.status] != "failed")
            & (self._df[self._col_names.parsed_name] != "UNDEFINED")
        ]

        self._failure_df: pd.DataFrame = self._df.loc[
            (self._df[self._col_names.status] == "failed")
            | (self._df[self._col_names.parsed_name] == "UNDEFINED")
        ]

    @classmethod
    def from_csv_input(
        cls,
        csv_input: Path | TextIO,
        col_names: ParsedDSColNames | None = None,
        fillna: Any = None,
    ) -> Self:
        """Initialise dataset from CSV input.
        :param csv_input: CSV input.
        :param name: Dataset name.
        :param fillna: Value to fill NaN values with.
        :returns: Dataset.
        """
        if isinstance(csv_input, Path):
            logger.info(f"Read dataset from: {csv_input}")
        else:
            logger.info("Read dataset from file-like object.")

        df: pd.DataFrame = pd.read_csv(
            csv_input, index_col=0, sep=",", dtype="string"
        )

        if fillna is not None:
            df.fillna(fillna, inplace=True)

        return cls(df, col_names)

    @property
    def success_index(self) -> pd.Index:
        return self._success_df.index

    @property
    def success_ds(self) -> Self:
        return type(self)(self._success_df, self._col_names)

    @property
    def failure_ds(self) -> Self:
        return type(self)(self._failure_df, self._col_names)

    @property
    def failure_index(self) -> pd.Index:
        return self._failure_df.index

    @property
    def index_name(self) -> str:
        return self._df.index.name

    @property
    def col_names(self) -> ParsedDSColNames:
        return self._col_names

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def parsed_names(self) -> pd.Series:
        return self._df[self._col_names.parsed_name]

    @property
    def original_names(self) -> pd.Series:
        return self._df[self._col_names.original_name]

    @property
    def name_df(self) -> pd.DataFrame:
        return self._df[
            [
                self._col_names.parsed_name,
                self._col_names.original_name,
            ]
        ]

    @property
    def name_level_df(self) -> pd.DataFrame:
        return self._df[
            [
                self._col_names.parsed_name,
                self._col_names.original_name,
                self._col_names.level,
            ]
        ]

    @property
    def classification_df(self) -> pd.DataFrame:
        return self._df[
            [
                self._col_names.category,
                self._col_names.class_,
                self._col_names.species,
                self._col_names.molecular_species,
                self._col_names.sn_position,
                self._col_names.structure_defined,
                self._col_names.full_structure,
                self._col_names.complete_structure,
            ]
        ]

    @property
    def fas(self) -> pd.DataFrame:
        return self._df[
            [
                self._col_names.fa1,
                self._col_names.fa2,
                self._col_names.fa3,
                self._col_names.fa4,
            ]
        ]

    @property
    def lcb(self) -> pd.Series:
        return self._df[self._col_names.lcb]

    @property
    def components(self) -> pd.DataFrame:
        return self._df[
            [
                self._col_names.fa1,
                self._col_names.fa2,
                self._col_names.fa3,
                self._col_names.fa4,
                self._col_names.lcb,
            ]
        ]

    def concat_ds(self, other: Self) -> Self:
        """Concatenate two datasets.
        :param other: Other dataset.
        :returns: Concatenated dataset.
        """
        df: pd.DataFrame = pd.concat([self._df, other._df])

        return self.__class__(df)

    def get_subset(self, index: pd.Index, intersection: bool = False) -> Self:
        """Get subset of dataset.
        :param index: Index of subset.
        :returns: Subset of dataset.
        """
        if intersection:
            index = index.intersection(self._df.index)
        elif not set(index).issubset(set(self._df.index)):
            raise ValueError("Index is not a subset of the dataset index.")

        df: pd.DataFrame = self._df.loc[index]
        df.index.rename(self._df.index.name, inplace=True)

        return self.__class__(df)

    def get_component_complete_subset(self) -> Self:
        """Get subset of dataset with complete components.
        :returns: Subset of dataset.
        """
        has_no_missing_components: pd.Series = ~self.components.apply(
            lambda row: "MISSING" in row.values, axis="columns"
        )

        must_have_lcb: pd.Series = self._df[self.col_names.category] == "SP"

        has_no_lcb: pd.Series = self._df[self.col_names.lcb].fillna("") == ""

        lcb_based_filter: pd.Series = ~(must_have_lcb & has_no_lcb)

        fa_excempt: pd.Series = self._df[self.col_names.category].isin(
            ["ST", "PK", "PL"]
        ) & ~self._df[self.col_names.class_].str.startswith("CE") | self._df[
            self.col_names.class_
        ].str.startswith(
            "SPB"
        )

        has_no_fa: pd.Series = (self.fas.fillna("") == "").all(axis=1)

        fa_based_filter: pd.Series = fa_excempt | ~has_no_fa

        complete_filter: pd.Series = (
            has_no_missing_components & lcb_based_filter & fa_based_filter
        )

        subset_df: pd.DataFrame = self._df[complete_filter]

        return type(self)(subset_df)

    @classmethod
    def _validate_df(
        cls, df: pd.DataFrame, col_names: ParsedDSColNames
    ) -> None:
        if df.index.name != col_names.index:
            raise ValueError(
                f"Index name is {df.index.name} but "
                f"should be {col_names.index}."
            )

        missing_columns: set = cls._determine_missing_column_names(
            df, col_names
        )

        if missing_columns:
            raise ValueError(f"Missing columns in dataset: {missing_columns}")

    @classmethod
    def _determine_missing_column_names(
        cls, df: pd.DataFrame, col_names: ParsedDSColNames
    ) -> set:
        missing_columns: set = set(col_names.col_names_list).difference(
            set(df.reset_index().columns)
        )

        return missing_columns


def parse_name_series(
    names: pd.Series,
    notation: str = "all",
    parsed_lipid_feature_names: ParsedLipidFeatureNames | None = None,
    lipid_parsing_outcome_texts: LipidParsingOutcomeTexts | None = None,
    component_missing_labels: ComponentMissingLabels | None = None,
    index_name: str = "INDEX",
) -> ParsedDataset:
    """Parse a series of lipid names and add additional
    information about names at different notation levels
    and components to the resulting dataframe.
    :param names: Series of lipid names.
    :param notation: Lipid shorthand notation style.
    :param parsed_lipid_feature_names: Parsed lipid feature names.
    :param lipid_parsing_outcome_texts: Lipid parsing outcome texts.
    :param component_missing_labels: Component missing labels.
    :return: Dataset containing the parsed notation as well as
        class and component information.
    """
    if parsed_lipid_feature_names is None:
        parsed_lipid_feature_names = ParsedLipidFeatureNames()
    if lipid_parsing_outcome_texts is None:
        lipid_parsing_outcome_texts = LipidParsingOutcomeTexts()
    if component_missing_labels is None:
        component_missing_labels = ComponentMissingLabels()

    parser: Parser = _get_parser(notation)

    parsed_df: pd.DataFrame = _gen_parsed_df(
        names,
        parser,
        parsed_lipid_feature_names,
        lipid_parsing_outcome_texts,
        component_missing_labels,
        index_name,
    )

    parsed_ds_col_names: ParsedDSColNames = ParsedDSColNames(
        index=index_name, **asdict(parsed_lipid_feature_names)
    )

    parsed_ds: ParsedDataset = ParsedDataset(parsed_df, parsed_ds_col_names)

    return parsed_ds


def _get_parser(notation: str) -> Parser:
    parsers: dict[str, type[Parser]] = {
        "all": LipidParser,
        "goslin": GoslinParser,
        "lmsd": LipidMapsParser,
        "sl": SwissLipidsParser,
    }

    if notation not in parsers:
        raise ValueError(
            f"Invalid notation style: {notation}, "
            f"options are {', '.join(parsers.keys())}"
        )

    parser: Parser = parsers[notation]()

    return parser


def _gen_parsed_df(
    names: pd.Series,
    parser: Parser,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
    lipid_parsing_outcome_texts: LipidParsingOutcomeTexts,
    component_missing_labels: ComponentMissingLabels,
    index_name: str,
) -> pd.DataFrame:
    parsed_df: pd.DataFrame = (
        names.copy()
        .progress_apply(
            _parse_name_and_extract_info,
            parser=parser,
            parsed_lipid_feature_names=parsed_lipid_feature_names,
            lipid_parsing_outcome_texts=lipid_parsing_outcome_texts,
            component_missing_labels=component_missing_labels,
        )
        .astype("string")
        .fillna("")
    )

    parsed_df.index = parsed_df.index.rename(index_name).astype("string")

    return parsed_df


def _parse_name_and_extract_info(
    name: str,
    parser: Parser,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
    lipid_parsing_outcome_texts: LipidParsingOutcomeTexts,
    component_missing_labels: ComponentMissingLabels,
) -> pd.Series:
    parsing_results: LipidParsingResults = _parse_name(
        name, parser, lipid_parsing_outcome_texts
    )

    info_dict = (
        _get_success_info(
            parsing_results,
            parsed_lipid_feature_names,
            component_missing_labels,
        )
        if parsing_results.status == lipid_parsing_outcome_texts.success_label
        else _get_failure_info(parsing_results, parsed_lipid_feature_names)
    )

    formatted_info_dict: dict[str, str] = _format_info_dict(
        info_dict, parsed_lipid_feature_names
    )

    return pd.Series(formatted_info_dict)


def _format_info_dict(
    info_dict: dict[str, str],
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
) -> dict[str, str]:
    formatted_info_dict: dict[str, str] = {
        feature: info_dict.get(feature, "")
        for feature in parsed_lipid_feature_names.col_names_list
    }

    return formatted_info_dict


def _parse_name(
    name: str,
    parser: Parser,
    lipid_parsing_outcome_texts: LipidParsingOutcomeTexts,
) -> LipidParsingResults:
    if _is_name_missing(name):
        results = _gen_name_missing_parsing_results(
            name, lipid_parsing_outcome_texts
        )
    else:
        results = _gen_name_present_parsing_results(
            name, parser, lipid_parsing_outcome_texts
        )

    return results


def _is_name_missing(name: str) -> bool:
    return name == ""


def _gen_name_missing_parsing_results(
    name: str,
    lipid_parsing_outcome_texts: LipidParsingOutcomeTexts,
) -> LipidParsingResults:
    return LipidParsingResults(
        name,
        None,
        lipid_parsing_outcome_texts.failure_label,
        lipid_parsing_outcome_texts.failure_message_missing,
    )


def _gen_name_present_parsing_results(
    name: str,
    parser: Parser,
    lipid_parsing_outcome_texts: LipidParsingOutcomeTexts,
) -> LipidParsingResults:
    try:
        lipid: LipidAdduct = parser.parse(name)
        results = LipidParsingResults(
            name,
            lipid,
            lipid_parsing_outcome_texts.success_label,
            lipid_parsing_outcome_texts.success_message,
        )
    except Exception as e:
        results = LipidParsingResults(
            name,
            None,
            lipid_parsing_outcome_texts.failure_label,
            f"{lipid_parsing_outcome_texts.failure_message_not_parsed}: {str(e)}",  # noqa E501
        )

    return results


def _get_failure_info(
    parsing_results: LipidParsingResults,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
) -> dict[str, str]:
    return {
        parsed_lipid_feature_names.original_name: parsing_results.original_name,  # noqa E501
        parsed_lipid_feature_names.status: parsing_results.status,
        parsed_lipid_feature_names.message: parsing_results.message,
    }


def _get_success_info(
    parsing_results: LipidParsingResults,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
    component_missing_labels: ComponentMissingLabels,
) -> dict[str, str]:
    if parsing_results.lipid is None:
        raise ValueError("Lipid object is None.")

    lipid: LipidAdduct = parsing_results.lipid

    info: dict[str, str] = (
        _get_name_dict(
            parsing_results.original_name, lipid, parsed_lipid_feature_names
        )
        | _get_components(
            lipid, parsed_lipid_feature_names, component_missing_labels
        )
        | _get_level_dict(lipid, parsed_lipid_feature_names)
    )

    return info


def _get_name_dict(
    original_name: str,
    lipid: LipidAdduct,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
) -> dict[str, str]:
    names: dict[str, str] = {
        parsed_lipid_feature_names.original_name: original_name,
        parsed_lipid_feature_names.parsed_name: lipid.get_lipid_string(),
    }

    return names


def _get_level_dict(
    lipid: LipidAdduct,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
) -> dict[str, str]:
    level: dict[str, str] = {
        parsed_lipid_feature_names.level: lipid.lipid.info.level.name  # type: ignore # noqa E501
    }

    level_names: dict[str, str] = {
        level.name: (
            lipid.get_lipid_string(level)
            if (level.value <= lipid.lipid.info.level.value)  # type: ignore
            else LipidLevel.UNDEFINED.name
        )
        for level in LipidLevel
        if level != LipidLevel.UNDEFINED
    }

    level_info: dict[str, str] = level | level_names

    return level_info


def _get_components(
    lipid: LipidAdduct,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
    component_missing_labels: ComponentMissingLabels,
) -> dict[str, str]:
    component_dict: dict[str, FattyAcid] = _get_component_dict(lipid)

    fas: dict[str, str] = _get_fa_components(
        lipid,
        parsed_lipid_feature_names,
        component_dict,
        component_missing_labels,
    )

    lcbs: dict[str, str] = _get_lcb_component(
        lipid,
        parsed_lipid_feature_names,
        component_dict,
        component_missing_labels,
    )

    components: dict[str, str] = fas | lcbs

    return components


def _get_fa_components(
    lipid: LipidAdduct,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
    component_dict: dict[str, FattyAcid],
    component_missing_labels: ComponentMissingLabels,
) -> dict[str, str]:
    expected_num_fa: int = _get_expected_num_fa(lipid)

    fas: dict[str, str] = {}

    for key in parsed_lipid_feature_names.fas[:expected_num_fa]:
        if key in component_dict:
            fas[key] = component_dict[key].to_string(
                LipidLevel.COMPLETE_STRUCTURE
            )
        else:
            fas[key] = component_missing_labels.missing

    for key in parsed_lipid_feature_names.fas[expected_num_fa:]:
        fas[key] = component_missing_labels.not_applicable

    return fas


def _get_lcb_component(
    lipid: LipidAdduct,
    parsed_lipid_feature_names: ParsedLipidFeatureNames,
    component_dict: dict[str, FattyAcid],
    component_missing_labels: ComponentMissingLabels,
) -> dict[str, str]:
    lcbs: dict[str, str] = {}

    if _has_lcb(lipid):
        if parsed_lipid_feature_names.lcb in component_dict:
            lcbs[parsed_lipid_feature_names.lcb] = component_dict[
                parsed_lipid_feature_names.lcb
            ].to_string(LipidLevel.COMPLETE_STRUCTURE)
        else:
            lcbs[parsed_lipid_feature_names.lcb] = (
                component_missing_labels.missing
            )
    else:
        lcbs[parsed_lipid_feature_names.lcb] = (
            component_missing_labels.not_applicable
        )

    return lcbs


def _get_component_dict(lipid: LipidAdduct) -> dict[str, FattyAcid]:
    return lipid.lipid.fa if hasattr(lipid.lipid, "fa") else {}  # type: ignore


def _has_lcb(lipid: LipidAdduct) -> bool:
    return lipid.get_lipid_string(LipidLevel.CATEGORY) == LipidCategory.SP.name


def _get_expected_num_fa(lipid: LipidAdduct) -> int:
    expected_num_fa: int = lipid.lipid.info.total_fa  # type: ignore

    if _has_lcb(lipid):
        expected_num_fa -= 1

    return expected_num_fa
