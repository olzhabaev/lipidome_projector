"""Module concerning the handling of lipidome data."""

import base64
import io
import logging

from dataclasses import dataclass

from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset
from lipid_data_processing.notation.matching import ConstraintsDataset
from lipid_data_processing.notation.matching_summary import MatchingSummary

from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.database.in_memory_df_db import (
    InMemoryDataFrameDB,
)
from lipidome_projector.lipidome.lipidome_ds_postprocessing import (
    process_lipidome_ds,
)
from lipidome_projector.lipidome.lipidome_vector_matching import (
    perf_vector_matching,
)
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.lipidome_front_end_data import (
    LipidomeFrontEndData,
)
from lipidome_projector.lipidome.translation import (
    lipidome_ds_to_lipidome_fe_data,
)


logger: logging.Logger = logging.getLogger(__name__)

# TODO: Simplify and utilize / introduce abstractions.


@dataclass(frozen=True)
class LipidomeUploadOutput:
    lipidome_fe_data: LipidomeFrontEndData
    failures_records: list[dict]
    failures_column_defs: list[dict]
    processing_failure: bool
    failure_message: str


def process_lipidome_upload(
    name,
    abundances_contents: str,
    lipidome_features_contents: str,
    fa_constraints_contents: str,
    lcb_constraints_contents: str,
    database: BaseDB,
    col_names: ColNames,
) -> LipidomeUploadOutput:
    """Process the lipidome upload.
    :param name: Name of the lipidome.
    :param abundances_contents: Contents of the abundances file.
    :param lipidome_features_contents: Contents of the lipidome
        features file.
    :param fa_constraints_contents: Contents of the FA constraints file.
    :param lcb_constraints_contents: Contents of the LCB constraints
        file.
    :param database: Database to use for matching.
    :param col_names: Column names.
    :return: Lipidome upload output.
    """
    try:
        lipidome_output: LipidomeUploadOutput = (
            _attempt_process_lipidome_upload(
                name=name,
                abundances_contents=abundances_contents,
                lipidome_features_contents=lipidome_features_contents,
                fa_constraints_contents=fa_constraints_contents,
                lcb_constraints_contents=lcb_constraints_contents,
                database=database,
                col_names=col_names,
            )
        )
    except Exception as e:
        lipidome_output = LipidomeUploadOutput(
            lipidome_fe_data=LipidomeFrontEndData(),
            failures_records=list(),
            failures_column_defs=list(),
            processing_failure=True,
            failure_message=str(e),
        )

    return lipidome_output


def _attempt_process_lipidome_upload(
    name,
    abundances_contents: str,
    lipidome_features_contents: str,
    fa_constraints_contents: str,
    lcb_constraints_contents: str,
    database: BaseDB,
    col_names: ColNames,
) -> LipidomeUploadOutput:
    lipidome_ds: LipidomeDataset
    matching_summary: MatchingSummary
    lipidome_ds, matching_summary = _gen_and_match_ds(
        name=name,
        abundances_contents=abundances_contents,
        lipidome_features_contents=lipidome_features_contents,
        fa_constraints_contents=fa_constraints_contents,
        lcb_constraints_contents=lcb_constraints_contents,
        database=database,
        lipid_col_name=col_names.lipid,
    )

    failures_records: list[dict]
    failures_column_defs: list[dict]
    failures_records, failures_column_defs = _get_failrues_grid_data(
        matching_summary
    )

    process_lipidome_ds(lipidome_ds, col_names)

    lipidome_fe_data: LipidomeFrontEndData = lipidome_ds_to_lipidome_fe_data(
        lipidome_ds, col_names
    )

    return LipidomeUploadOutput(
        lipidome_fe_data=lipidome_fe_data,
        failures_records=failures_records,
        failures_column_defs=failures_column_defs,
        processing_failure=False,
        failure_message="",
    )


def _gen_and_match_ds(
    name: str,
    abundances_contents: str,
    lipidome_features_contents: str,
    fa_constraints_contents: str,
    lcb_constraints_contents: str,
    database: BaseDB,
    lipid_col_name: str,
) -> tuple[LipidomeDataset, MatchingSummary]:
    datasets: tuple[LipidomeDataset, ConstraintsDataset] = (
        _generate_base_datasets(
            name=name,
            abundances_contents=abundances_contents,
            lipidome_features_contents=lipidome_features_contents,
            fa_constraints_contents=fa_constraints_contents,
            lcb_constraints_contents=lcb_constraints_contents,
        )
    )

    lipidome_ds: LipidomeDataset
    matching_summary: MatchingSummary
    lipidome_ds, matching_summary = match(*datasets, database, lipid_col_name)

    return lipidome_ds, matching_summary


def _generate_base_datasets(
    name,
    abundances_contents: str,
    lipidome_features_contents: str,
    fa_constraints_contents: str,
    lcb_constraints_contents: str,
) -> tuple[LipidomeDataset, ConstraintsDataset]:
    lipidome_ds: LipidomeDataset = _gen_lipidome_ds(
        name=name,
        abundances_contents=abundances_contents,
        lipidome_features_contents=lipidome_features_contents,
    )

    constraints_ds: ConstraintsDataset = _gen_constraints_ds(
        fa_constraints_contents=fa_constraints_contents,
        lcb_constraints_contents=lcb_constraints_contents,
    )

    return lipidome_ds, constraints_ds


def _gen_lipidome_ds(
    name: str,
    abundances_contents: str,
    lipidome_features_contents: str,
) -> LipidomeDataset:
    abundances_string_io: io.StringIO = _get_string_io_from_contents(
        abundances_contents
    )
    lipidome_features_string_io: io.StringIO = _get_string_io_from_contents(
        lipidome_features_contents
    )
    lipidome_ds: LipidomeDataset = LipidomeDataset.from_csv_input(
        name=name,
        abundances_csv_path_or_string_io=abundances_string_io,
        lipidome_features_csv_path_or_string_io=lipidome_features_string_io,
    )
    abundances_string_io.close()
    lipidome_features_string_io.close()

    return lipidome_ds


def _gen_constraints_ds(
    fa_constraints_contents: str,
    lcb_constraints_contents: str,
) -> ConstraintsDataset:
    fa_constraints_string_io: io.StringIO = _get_string_io_from_contents(
        fa_constraints_contents
    )
    lcb_constraints_string_io: io.StringIO = _get_string_io_from_contents(
        lcb_constraints_contents
    )
    constraints_ds: ConstraintsDataset = (
        ConstraintsDataset.from_constraint_csv_input(
            fa_constraints_csv_input=fa_constraints_string_io,
            lcb_constraints_csv_input=lcb_constraints_string_io,
        )
    )
    fa_constraints_string_io.close()
    lcb_constraints_string_io.close()

    return constraints_ds


def _get_string_io_from_contents(
    contents: str,
) -> io.StringIO:
    contents_decoded: str = base64.b64decode(contents.split(",")[1]).decode()

    return io.StringIO(contents_decoded)


def match(
    lipidome_ds: LipidomeDataset,
    constraints_ds: ConstraintsDataset,
    database: BaseDB,
    lipid_col_name: str,
) -> tuple[LipidomeDataset, MatchingSummary]:
    """Perform matching.
    :param lipidome_ds: Lipidome dataset.
    :param constraints_ds: Constraints dataset.
    :param database: Database to use for matching.
    :return: Lipidome dataset and matching summary.
    """
    if isinstance(database, InMemoryDataFrameDB):
        matching_results: tuple[LipidomeDataset, MatchingSummary] = (
            _perform_in_memory_matching(
                lipidome_ds, constraints_ds, database, lipid_col_name
            )
        )
    else:
        raise ValueError(
            f"Database type {type(database)} not supported for vector "
            "lipidome dataset generation."
        )

    return matching_results


def _perform_in_memory_matching(
    lipidome_ds: LipidomeDataset,
    constraints_ds: ConstraintsDataset,
    database: InMemoryDataFrameDB,
    lipid_col_name: str,
) -> tuple[LipidomeDataset, MatchingSummary]:
    return perf_vector_matching(
        lipidome_ds=lipidome_ds,
        constraints_ds=constraints_ds,
        database_matching_ds=database.matching_ds,
        isomer_vectors_df=database.vectors_combined,
        isomer_smiles=database.smiles,
        lipid_col_name=lipid_col_name,
    )


def _get_failrues_grid_data(
    matching_summary: MatchingSummary,
) -> tuple[list[dict], list[dict]]:
    failures_records: list[dict] = matching_summary.failures.to_dict("records")

    failures_column_defs: list[dict] = [
        {
            "field": name,
            "filter": True,
            "floatingFilter": True,
            "sortable": True,
            "columnGroupShow": "open",
        }
        for name in matching_summary.failures.columns
    ]

    return failures_records, failures_column_defs
