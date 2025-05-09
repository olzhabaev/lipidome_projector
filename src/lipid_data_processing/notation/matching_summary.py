"""Module concerning lipid dataset matching results."""

import logging

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from lipid_data_processing.notation.parsing import ParsedDataset
from lipid_data_processing.notation.matching import MatchingResults


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MatchingSummary:
    dataset_name: str
    database_name: str

    matching_dataset: ParsedDataset
    matching_results: MatchingResults

    failures: pd.DataFrame = field(init=False)

    num_lipids: int = field(init=False)
    num_parsing_failures: int = field(init=False)
    num_parsed_no_match_lipids: int = field(init=False)
    num_original_name_no_match_lipids: int = field(init=False)
    num_filtered_lipids: int = field(init=False)
    num_failures: int = field(init=False)
    failure_proportion: float = field(init=False)

    summary_dict: dict = field(init=False)
    print_dict: dict = field(init=False)
    print_string: str = field(init=False)

    failure_reason_column_name: str = field(init=False, default="REASON")

    def __post_init__(self) -> None:
        self._set_statistics()
        self._derive_field("summary_dict", self._build_summary_dict())
        self._derive_field("print_dict", self._build_print_dict())
        self._derive_field("print_string", self._build_print_string())
        self._derive_field(
            "failures",
            self._compile_failures(
                self.matching_results, self.matching_dataset
            ),
        )

    def __str__(self) -> str:
        return self.print_string

    def _derive_field(self, field_name: str, value: Any) -> None:
        object.__setattr__(self, field_name, value)

    def _set_statistics(self) -> None:
        num_lipids: int = len(self.matching_dataset.original_names)
        self._derive_field("num_lipids", num_lipids)

        num_parsing_failures: int = len(self.matching_dataset.failure_ds.df)
        self._derive_field("num_parsing_failures", num_parsing_failures)

        num_parsed_no_match_lipids: int = len(
            self.matching_results.parsed_no_match.dataframe
        )
        self._derive_field(
            "num_parsed_no_match_lipids", num_parsed_no_match_lipids
        )

        num_original_name_no_match_lipids: int = len(
            self.matching_results.original_name_no_match.dataframe
        )
        self._derive_field(
            "num_original_name_no_match_lipids",
            num_original_name_no_match_lipids,
        )

        num_filtered_lipids: int = len(
            self.matching_results.filtered_lipids.dataframe
        )
        self._derive_field("num_filtered_lipids", num_filtered_lipids)

        num_failures: int = (
            num_parsed_no_match_lipids
            + num_original_name_no_match_lipids
            + num_filtered_lipids
        )
        self._derive_field("num_failures", num_failures)

        failure_proportion: float = num_failures / num_lipids
        self._derive_field("failure_proportion", failure_proportion)

    def _build_summary_dict(self) -> dict:
        summary_dict: dict = {
            "num_lipids": self.num_lipids,
            "num_failures": self.num_failures,
            "failure_proportion": self.failure_proportion,
            "num_parsing_failures": self.num_parsing_failures,
            "num_parsed_no_match_lipids": self.num_parsed_no_match_lipids,
            "num_original_name_no_match_lipids": (
                self.num_original_name_no_match_lipids
            ),
            "num_filtered_lipids": self.num_filtered_lipids,
        }

        return summary_dict

    def _build_print_dict(self) -> dict:
        print_dict: dict = {
            "Dataset name": f"{self.dataset_name}",
            "Database name": f"{self.database_name}",
            "Number of lipids": f"{self.summary_dict['num_lipids']}",
            "Number of failures": f"{self.summary_dict['num_failures']}",
            "Failure proportion": (
                f"{100 * self.summary_dict['failure_proportion']:.4f}%"
            ),
            "Number of parsing failures": (
                f"{self.summary_dict['num_parsing_failures']}"
            ),
            "Number of parsed no match lipids": (
                f"{self.summary_dict['num_parsed_no_match_lipids']}"
            ),
            "Number of original name no match lipids": (
                f"{self.summary_dict['num_original_name_no_match_lipids']}"
            ),
            "Number of filtered lipids": (
                f"{self.summary_dict['num_filtered_lipids']}"
            ),
        }

        return print_dict

    def _build_print_string(self) -> str:
        print_string: str = "\n".join(
            f"{key}: {value}" for key, value in self.print_dict.items()
        )

        return print_string

    @classmethod
    def _compile_failures(
        cls,
        matching_results: MatchingResults,
        matching_dataset: ParsedDataset,
    ) -> pd.DataFrame:
        parsed_no_match_lipids: pd.DataFrame = (
            cls._compile_parsed_no_match_lipids(
                matching_results, matching_dataset
            )
        )

        original_name_no_match_lipids: pd.DataFrame = (
            cls._compile_original_name_no_match_lipids(
                matching_results, matching_dataset
            )
        )

        failure_groups: list[pd.DataFrame] = [
            df
            for df in (
                parsed_no_match_lipids,
                original_name_no_match_lipids,
                matching_results.filtered_lipids.dataframe,
            )
            if not df.empty
        ]

        failures: pd.DataFrame = (
            pd.concat(
                failure_groups,
                ignore_index=True,
            )
            if failure_groups
            else pd.DataFrame()
        )

        return failures

    @classmethod
    def _compile_parsed_no_match_lipids(
        cls,
        matching_results: MatchingResults,
        matching_dataset: ParsedDataset,
    ) -> pd.DataFrame:
        parsed_no_match_lipids: pd.DataFrame = pd.DataFrame(
            {
                matching_dataset.col_names.original_name: (
                    matching_results.parsed_no_match.dataframe[
                        matching_dataset.col_names.original_name
                    ]
                ),
                matching_dataset.col_names.parsed_name: (
                    matching_results.parsed_no_match.dataframe[
                        matching_dataset.col_names.parsed_name
                    ]
                ),
                cls.failure_reason_column_name: "Parsed but no matches.",
            }
        )

        return parsed_no_match_lipids

    @classmethod
    def _compile_original_name_no_match_lipids(
        cls,
        matching_results: MatchingResults,
        matching_dataset: ParsedDataset,
    ) -> pd.DataFrame:
        original_name_no_match_lipids: pd.DataFrame = pd.DataFrame(
            {
                matching_dataset.col_names.original_name: (
                    matching_results.original_name_no_match.dataframe[
                        matching_dataset.col_names.original_name
                    ]
                ),
                cls.failure_reason_column_name: (
                    "Parsing failed and no original name matches."
                ),
            }
        )

        return original_name_no_match_lipids

    def write_matching_summary_xls(
        self,
        path: str,
        fa_constraints: pd.Series,
        lcb_constraints: pd.Series,
    ) -> None:
        """Write parsing and matching results to an XLS file.
        :param path: Path to xls file.
        :param matching_summary: Parsing & matching summary object.
        :fa_constraints: Series of utilised FA constraints.
        :lcb_constraints: Series of utilised LCB constraints.
        """

        sheets: dict = self._compile_sheets(fa_constraints, lcb_constraints)

        with pd.ExcelWriter(path) as writer:
            for name, content_df in sheets.items():
                self._write_sheet(name, content_df, writer)

    def _compile_sheets(
        self,
        fa_constraints: pd.Series,
        lcb_constraints: pd.Series,
    ) -> dict:
        summary_df: pd.DataFrame = (
            pd.Series(self.print_dict)
            .to_frame()
            .reset_index()
            .rename(columns={"index": "feature", 0: "value"})
        )

        return {
            "summary": summary_df,
            "matched_isomers": (
                self.matching_results.constrained_matches_info.dataframe
            ),
            "failures": self.failures,
            "fa_constraints": fa_constraints.rename("FA").to_frame(),
            "lcb_constraints": lcb_constraints.rename("LCB").to_frame(),
        }

    @staticmethod
    def _write_sheet(
        name: str, df: pd.DataFrame, writer: pd.ExcelWriter
    ) -> None:
        df.to_excel(excel_writer=writer, sheet_name=name, index=False)

        for column in df.columns:
            column_width = max(
                df[column].astype(str).map(len).max(), len(column)
            )
            col_idx = df.columns.get_loc(column)
            writer.sheets[name].set_column(col_idx, col_idx, column_width)
