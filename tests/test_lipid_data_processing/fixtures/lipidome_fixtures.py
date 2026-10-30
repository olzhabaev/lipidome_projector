"""Module concerning lipidome fixtures."""

import logging

from io import StringIO
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import pytest

from _pytest.tmpdir import TempPathFactory

from lipid_data_processing.lipidomes.lipidome_abundances import (
    LipidomeAbundances,
)

from lipid_data_processing.lipidomes.lipidome_abundance_changes import (
    AbundanceChangeStorage,
)
from lipid_data_processing.lipidomes.lipid_features import LipidFeatures
from lipid_data_processing.lipidomes.lipidome_features import LipidomeFeatures

from tests.test_lipid_data_processing.fixtures.high_level_lipid_fixtures import *  # noqa F403, E501
from tests.test_lipid_data_processing.util.lipid_description import (
    LipidDescription,
    LipidCollection,
)
from tests.test_lipid_data_processing.util.lipidome_description import (
    DatasetAbundancesDescription,
    AbundanceRowDescription,
    AbundancesAggregationTestData,
    AbundancesChangeRowDescription,
    DatasetAbundancesChangeDescription,
    AbundanceChangeStorageDescription,
    LipidomeFeaturesRowDescription,
    DatasetLipidomeFeaturesDescription,
    LipidomeFeaturesAggregationTestData,
    LipidomeFeaturesAddFeatureTestData,
    LipidomeDatasetDescription,
)

logger: logging.Logger = logging.getLogger(__name__)


# * SAMPLE DESCRIPTIONS -----------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_s_0_name() -> str:
    return "lipidome_sample_0"


@pytest.fixture(scope="session")
def ld_0_s_1_name() -> str:
    return "lipidome_sample_1"


@pytest.fixture(scope="session")
def ld_0_s_2_name() -> str:
    return "lipidome_sample_2"


@pytest.fixture(scope="session")
def ld_0_s_3_name() -> str:
    return "lipidome_sample_3"


@pytest.fixture(scope="session")
def ld_0_s_4_name() -> str:
    return "lipidome_sample_4"


@pytest.fixture(scope="session")
def ld_0_lipidome_sample_names(
    ld_0_s_0_name: str,
    ld_0_s_1_name: str,
    ld_0_s_2_name: str,
    ld_0_s_3_name: str,
    ld_0_s_4_name: str,
) -> pd.Index:
    return pd.Index(
        [
            ld_0_s_0_name,
            ld_0_s_1_name,
            ld_0_s_2_name,
            ld_0_s_3_name,
            ld_0_s_4_name,
        ]
    )


# * LIPIDS ------------------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_lipids_collection(
    dg_sp_24_0: LipidDescription,
    dg_sp_24_2: LipidDescription,
    pc_sp_34_4: LipidDescription,
    cer_sp_34_1_2: LipidDescription,
    teasterone: LipidDescription,
) -> LipidCollection:
    return LipidCollection(
        [
            dg_sp_24_0,
            dg_sp_24_2,
            pc_sp_34_4,
            cer_sp_34_1_2,
            teasterone,
        ]
    )


@pytest.fixture(scope="session")
def ld_0_lipids(ld_0_lipids_collection: LipidCollection) -> pd.Index:
    return pd.Index(
        ld_0_lipids_collection.to_original_name_series(), dtype="object"
    )


# * ABUNDANCES --------------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_s_0_abundance_row(
    ld_0_s_0_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundanceRowDescription:
    return AbundanceRowDescription(
        sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: 0.1,
                ld_0_lipids_collection[2].original_name: 0.2,
                ld_0_lipids_collection[3].original_name: 0.3,
                ld_0_lipids_collection[4].original_name: 0.4,
            }
        ),
        string=f"{ld_0_s_0_name},nan,0.1,0.2,0.3,0.4",
    )


@pytest.fixture(scope="session")
def ld_0_s_1_abundance_row(
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundanceRowDescription:
    return AbundanceRowDescription(
        sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 1.0,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 1.2,
                ld_0_lipids_collection[3].original_name: 1.3,
                ld_0_lipids_collection[4].original_name: 1.4,
            }
        ),
        string=f"{ld_0_s_1_name},1.0,nan,1.2,1.3,1.4",
    )


@pytest.fixture(scope="session")
def ld_0_s_2_abundance_row(
    ld_0_s_2_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundanceRowDescription:
    return AbundanceRowDescription(
        sample_name=ld_0_s_2_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 2.0,
                ld_0_lipids_collection[1].original_name: 2.1,
                ld_0_lipids_collection[2].original_name: np.nan,
                ld_0_lipids_collection[3].original_name: 2.3,
                ld_0_lipids_collection[4].original_name: 2.4,
            }
        ),
        string=f"{ld_0_s_2_name},2.0,2.1,nan,2.3,2.4",
    )


@pytest.fixture(scope="session")
def ld_0_s_3_abundance_row(
    ld_0_s_3_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundanceRowDescription:
    return AbundanceRowDescription(
        sample_name=ld_0_s_3_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 3.0,
                ld_0_lipids_collection[1].original_name: 3.1,
                ld_0_lipids_collection[2].original_name: 3.2,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 3.4,
            }
        ),
        string=f"{ld_0_s_3_name},3.0,3.1,3.2,nan,3.4",
    )


@pytest.fixture(scope="session")
def ld_0_s_4_abundance_row(
    ld_0_s_4_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundanceRowDescription:
    return AbundanceRowDescription(
        sample_name=ld_0_s_4_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 4.0,
                ld_0_lipids_collection[1].original_name: 4.1,
                ld_0_lipids_collection[2].original_name: 4.2,
                ld_0_lipids_collection[3].original_name: 4.3,
                ld_0_lipids_collection[4].original_name: np.nan,
            }
        ),
        string=f"{ld_0_s_4_name},4.0,4.1,4.2,4.3,nan",
    )


@pytest.fixture(scope="session")
def ld_0_abundances_desc(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_2_abundance_row: AbundanceRowDescription,
    ld_0_s_3_abundance_row: AbundanceRowDescription,
    ld_0_s_4_abundance_row: AbundanceRowDescription,
    ld_0_lipids: pd.Index,
) -> DatasetAbundancesDescription:
    return DatasetAbundancesDescription(
        lipids=ld_0_lipids,
        row_descriptions=[
            ld_0_s_0_abundance_row,
            ld_0_s_1_abundance_row,
            ld_0_s_2_abundance_row,
            ld_0_s_3_abundance_row,
            ld_0_s_4_abundance_row,
        ],
    )


@pytest.fixture(scope="session")
def ld_0_abundances_str(
    ld_0_abundances_desc: DatasetAbundancesDescription,
) -> str:
    return ld_0_abundances_desc.to_str()


@pytest.fixture(scope="session")
def ld_0_abundances_tmp_file_path(
    tmp_path_factory: TempPathFactory,
    ld_0_abundances_str: str,
) -> Path:
    tmp_file_path = (
        tmp_path_factory.mktemp("lipidomes") / "ld_1_abundances.csv"
    )

    with open(tmp_file_path, "w") as f:
        f.write(ld_0_abundances_str)

    return tmp_file_path


@pytest.fixture(scope="function")
def ld_0_abundances_str_io(ld_0_abundances_str: str) -> StringIO:
    return StringIO(ld_0_abundances_str)


@pytest.fixture(scope="session")
def ld_0_abundances_df(
    ld_0_abundances_desc: DatasetAbundancesDescription,
) -> pd.DataFrame:
    return ld_0_abundances_desc.to_df()


@pytest.fixture(scope="session")
def ld_0_abundances(
    ld_0_abundances_df: pd.DataFrame,
) -> LipidomeAbundances:
    return LipidomeAbundances(ld_0_abundances_df)


# ** ABUNDANCES SUBSET -------------------------------------------------------


@pytest.fixture(
    scope="session",
    params=[[0, 1], [1, 2, 3], [3, 4]],
)
def integer_index_subset(request: pytest.FixtureRequest) -> list[int]:
    return request.param


@pytest.fixture(
    scope="session",
    params=[[0, 1], [1, 2, 3], [3, 4]],
)
def integer_column_subset(request: pytest.FixtureRequest) -> list[int]:
    return request.param


@pytest.fixture(scope="session")
def ld_0_subset(
    ld_0_abundances_desc: DatasetAbundancesDescription,
    integer_index_subset: list[int],
    integer_column_subset: list[int],
) -> DatasetAbundancesDescription:
    return ld_0_abundances_desc.get_subset(
        lipidome_indeces=integer_index_subset,
        lipid_indeces=integer_column_subset,
    )


@pytest.fixture(scope="session")
def ld_0_abundances_index_subset(
    ld_0_abundances_desc: DatasetAbundancesDescription,
    integer_index_subset: list[int],
) -> pd.Index:
    return pd.Index(
        ld_0_abundances_desc.row_descriptions[i].sample_name
        for i in integer_index_subset
    )


@pytest.fixture(scope="session")
def ld_0_abundances_column_subset(
    ld_0_lipids_collection: LipidCollection,
    integer_column_subset: list[int],
) -> pd.Index:
    return pd.Index(
        ld_0_lipids_collection[i].original_name for i in integer_column_subset
    )


@pytest.fixture(scope="session")
def ld_0_abundances_subset_df(
    ld_0_subset: DatasetAbundancesDescription,
) -> pd.DataFrame:
    return ld_0_subset.to_df()


# ** ABUNDANCES AGGREGATION --------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_abundances_get_aggregation_data_0(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_2_abundance_row: AbundanceRowDescription,
    ld_0_s_3_abundance_row: AbundanceRowDescription,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesAggregationTestData:
    nan_handling: Literal["skip", "zero"] = "skip"

    lipidome_indeces: list[pd.Index] = [
        pd.Index(
            [
                ld_0_s_0_abundance_row.sample_name,
                ld_0_s_1_abundance_row.sample_name,
            ]
        ),
        pd.Index(
            [
                ld_0_s_1_abundance_row.sample_name,
                ld_0_s_2_abundance_row.sample_name,
                ld_0_s_3_abundance_row.sample_name,
            ]
        ),
    ]

    lipidome_abundances: pd.DataFrame = pd.DataFrame(
        [
            {
                "INDEX": "mean_agg_0",
                ld_0_lipids_collection[0].original_name: 1.0,
                ld_0_lipids_collection[1].original_name: 0.1,
                ld_0_lipids_collection[2].original_name: 0.7,
                ld_0_lipids_collection[3].original_name: 0.8,
                ld_0_lipids_collection[4].original_name: 0.9,
            },
            {
                "INDEX": "mean_agg_1",
                ld_0_lipids_collection[0].original_name: 2.0,
                ld_0_lipids_collection[1].original_name: 2.6,
                ld_0_lipids_collection[2].original_name: 2.2,
                ld_0_lipids_collection[3].original_name: 1.8,
                ld_0_lipids_collection[4].original_name: 2.4,
            },
        ],
    ).set_index("INDEX")

    group_names: list[str] = ["mean_agg_0", "mean_agg_1"]

    return AbundancesAggregationTestData(
        lipidome_indices=lipidome_indeces,
        group_names=group_names,
        lipidome_abundances=LipidomeAbundances(lipidome_abundances),
        operation="mean",
        nan_handling=nan_handling,
    )


@pytest.fixture(scope="session")
def ld_0_abundances_add_aggregation_data_0(
    ld_0_abundances_get_aggregation_data_0: AbundancesAggregationTestData,  # noqa E501
    ld_0_abundances_df: pd.DataFrame,
) -> AbundancesAggregationTestData:
    abundances_df: pd.DataFrame = pd.concat(
        [
            ld_0_abundances_df,
            ld_0_abundances_get_aggregation_data_0.lipidome_abundances.df,  # noqa E501
        ]
    )
    return AbundancesAggregationTestData(
        lipidome_indices=ld_0_abundances_get_aggregation_data_0.lipidome_indices,  # noqa E501
        group_names=ld_0_abundances_get_aggregation_data_0.group_names,
        lipidome_abundances=LipidomeAbundances(abundances_df),
        operation=ld_0_abundances_get_aggregation_data_0.operation,
        nan_handling=ld_0_abundances_get_aggregation_data_0.nan_handling,  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_abundances_get_aggregation_data_1(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_2_abundance_row: AbundanceRowDescription,
    ld_0_s_3_abundance_row: AbundanceRowDescription,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesAggregationTestData:
    nan_handling: Literal["skip", "zero"] = "zero"

    lipidome_indeces: list[pd.Index] = [
        pd.Index(
            [
                ld_0_s_0_abundance_row.sample_name,
                ld_0_s_1_abundance_row.sample_name,
            ]
        ),
        pd.Index(
            [
                ld_0_s_1_abundance_row.sample_name,
                ld_0_s_2_abundance_row.sample_name,
                ld_0_s_3_abundance_row.sample_name,
            ]
        ),
    ]

    lipidome_abundances: pd.DataFrame = pd.DataFrame(
        [
            {
                "INDEX": "mean_agg_0",
                ld_0_lipids_collection[0].original_name: 0.5,
                ld_0_lipids_collection[1].original_name: 0.05,
                ld_0_lipids_collection[2].original_name: 0.7,
                ld_0_lipids_collection[3].original_name: 0.8,
                ld_0_lipids_collection[4].original_name: 0.9,
            },
            {
                "INDEX": "mean_agg_1",
                ld_0_lipids_collection[0].original_name: 2.0,
                ld_0_lipids_collection[1].original_name: 1.73333,
                ld_0_lipids_collection[2].original_name: 1.46666,
                ld_0_lipids_collection[3].original_name: 1.2,
                ld_0_lipids_collection[4].original_name: 2.4,
            },
        ],
    ).set_index("INDEX")

    group_names: list[str] = ["mean_agg_0", "mean_agg_1"]

    return AbundancesAggregationTestData(
        lipidome_indices=lipidome_indeces,
        group_names=group_names,
        lipidome_abundances=LipidomeAbundances(lipidome_abundances),
        operation="mean",
        nan_handling=nan_handling,
    )


@pytest.fixture(scope="session")
def ld_0_abundances_add_aggregation_data_1(
    ld_0_abundances_get_aggregation_data_1: AbundancesAggregationTestData,  # noqa E501
    ld_0_abundances_df: pd.DataFrame,
) -> AbundancesAggregationTestData:
    abundances_df: pd.DataFrame = pd.concat(
        [
            ld_0_abundances_df,
            ld_0_abundances_get_aggregation_data_1.lipidome_abundances.df,  # noqa E501
        ]
    )
    return AbundancesAggregationTestData(
        lipidome_indices=ld_0_abundances_get_aggregation_data_1.lipidome_indices,  # noqa E501
        group_names=ld_0_abundances_get_aggregation_data_1.group_names,
        lipidome_abundances=LipidomeAbundances(abundances_df),
        operation=ld_0_abundances_get_aggregation_data_1.operation,
        nan_handling=ld_0_abundances_get_aggregation_data_1.nan_handling,  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_abundances_get_aggregation_data_2(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_2_abundance_row: AbundanceRowDescription,
    ld_0_s_3_abundance_row: AbundanceRowDescription,
    ld_0_s_4_abundance_row: AbundanceRowDescription,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesAggregationTestData:
    lipidome_indeces: list[pd.Index] = [
        pd.Index(
            [
                ld_0_s_0_abundance_row.sample_name,
                ld_0_s_1_abundance_row.sample_name,
            ]
        ),
        pd.Index(
            [
                ld_0_s_2_abundance_row.sample_name,
                ld_0_s_3_abundance_row.sample_name,
                ld_0_s_4_abundance_row.sample_name,
            ]
        ),
    ]

    lipidome_abundances: pd.DataFrame = pd.DataFrame(
        [
            {
                "INDEX": "std_agg_0",
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 0.70710,
                ld_0_lipids_collection[3].original_name: 0.70710,
                ld_0_lipids_collection[4].original_name: 0.70710,
            },
            {
                "INDEX": "std_agg_1",
                ld_0_lipids_collection[0].original_name: 1.0,
                ld_0_lipids_collection[1].original_name: 1.0,
                ld_0_lipids_collection[2].original_name: 0.70710,
                ld_0_lipids_collection[3].original_name: 1.41421,
                ld_0_lipids_collection[4].original_name: 0.70710,
            },
        ],
    ).set_index("INDEX")

    group_names: list[str] = ["std_agg_0", "std_agg_1"]

    return AbundancesAggregationTestData(
        lipidome_indices=lipidome_indeces,
        group_names=group_names,
        lipidome_abundances=LipidomeAbundances(lipidome_abundances),
        operation="std",
        nan_handling="skip",
    )


@pytest.fixture(scope="session")
def ld_0_abundances_add_aggregation_data_2(
    ld_0_abundances_get_aggregation_data_2: AbundancesAggregationTestData,  # noqa E501
    ld_0_abundances_df: pd.DataFrame,
) -> AbundancesAggregationTestData:
    abundances_df: pd.DataFrame = pd.concat(
        [
            ld_0_abundances_df,
            ld_0_abundances_get_aggregation_data_2.lipidome_abundances.df,  # noqa E501
        ]
    )
    return AbundancesAggregationTestData(
        lipidome_indices=ld_0_abundances_get_aggregation_data_2.lipidome_indices,  # noqa E501
        group_names=ld_0_abundances_get_aggregation_data_2.group_names,
        lipidome_abundances=LipidomeAbundances(abundances_df),
        operation=ld_0_abundances_get_aggregation_data_2.operation,
        nan_handling=ld_0_abundances_get_aggregation_data_2.nan_handling,  # noqa E501
    )


# ** ABUNDANCES CHANGES -------------------------------------------------------

# *** DIFFERENCES -------------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_s_0_s_1_differences_row(
    ld_0_s_0_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_0_name,
        to_sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: -1.0,
                ld_0_lipids_collection[3].original_name: -1.0,
                ld_0_lipids_collection[4].original_name: -1.0,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_0_s_2_differences_row(
    ld_0_s_0_name: str,
    ld_0_s_2_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_0_name,
        to_sample_name=ld_0_s_2_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: -2,
                ld_0_lipids_collection[2].original_name: np.nan,
                ld_0_lipids_collection[3].original_name: -2.0,
                ld_0_lipids_collection[4].original_name: -2.0,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_2_s_0_differences_row(
    ld_0_s_2_name: str,
    ld_0_s_0_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_2_name,
        to_sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: 2,
                ld_0_lipids_collection[2].original_name: np.nan,
                ld_0_lipids_collection[3].original_name: 2.0,
                ld_0_lipids_collection[4].original_name: 2.0,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_1_s_0_differences_row(
    ld_0_s_0_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_1_name,
        to_sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 1.0,
                ld_0_lipids_collection[3].original_name: 1.0,
                ld_0_lipids_collection[4].original_name: 1.0,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_1_s_2_differences_row(
    ld_0_s_1_name: str,
    ld_0_s_2_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_1_name,
        to_sample_name=ld_0_s_2_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: -1.0,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: np.nan,
                ld_0_lipids_collection[3].original_name: -1.0,
                ld_0_lipids_collection[4].original_name: -1.0,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_2_s_1_differences_row(
    ld_0_s_2_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_2_name,
        to_sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 1.0,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: np.nan,
                ld_0_lipids_collection[3].original_name: 1.0,
                ld_0_lipids_collection[4].original_name: 1.0,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_differences_subset_desc_0(
    ld_0_s_0_s_1_differences_row: AbundancesChangeRowDescription,
    ld_0_s_0_s_2_differences_row: AbundancesChangeRowDescription,
    ld_0_s_1_s_0_differences_row: AbundancesChangeRowDescription,
    ld_0_s_1_s_2_differences_row: AbundancesChangeRowDescription,
    ld_0_s_2_s_0_differences_row: AbundancesChangeRowDescription,
    ld_0_s_2_s_1_differences_row: AbundancesChangeRowDescription,
) -> DatasetAbundancesChangeDescription:
    return DatasetAbundancesChangeDescription(
        changes=[
            ld_0_s_0_s_1_differences_row,
            ld_0_s_0_s_2_differences_row,
            ld_0_s_1_s_0_differences_row,
            ld_0_s_1_s_2_differences_row,
            ld_0_s_2_s_0_differences_row,
            ld_0_s_2_s_1_differences_row,
        ]
    )


@pytest.fixture(scope="session")
def ld_0_differences_subset_abundances_df_0(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_2_abundance_row: AbundanceRowDescription,
    ld_0_lipids: pd.Index,
) -> pd.DataFrame:
    return DatasetAbundancesDescription(
        lipids=ld_0_lipids,
        row_descriptions=[
            ld_0_s_0_abundance_row,
            ld_0_s_1_abundance_row,
            ld_0_s_2_abundance_row,
        ],
    ).to_df()


@pytest.fixture(scope="session")
def ld_0_differences_subset_df_0(
    ld_0_differences_subset_desc_0: DatasetAbundancesChangeDescription,
) -> pd.DataFrame:
    return ld_0_differences_subset_desc_0.to_df()


# *** FC ----------------------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_s_0_s_1_fc_row(
    ld_0_s_0_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_0_name,
        to_sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 0.1666666666,
                ld_0_lipids_collection[3].original_name: 0.2307692308,
                ld_0_lipids_collection[4].original_name: 0.2857142857,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_1_s_0_fc_row(
    ld_0_s_1_name: str,
    ld_0_s_0_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_1_name,
        to_sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 6,
                ld_0_lipids_collection[3].original_name: 4.33333,
                ld_0_lipids_collection[4].original_name: 3.5,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_0_s_3_fc_row(
    ld_0_s_0_name: str,
    ld_0_s_3_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_0_name,
        to_sample_name=ld_0_s_3_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: 0.0322580645,
                ld_0_lipids_collection[2].original_name: 0.0625,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 0.1176470588,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_3_s_0_fc_row(
    ld_0_s_3_name: str,
    ld_0_s_0_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_3_name,
        to_sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: 31,
                ld_0_lipids_collection[2].original_name: 16,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 8.5,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_1_s_3_fc_row(
    ld_0_s_1_name: str,
    ld_0_s_3_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_1_name,
        to_sample_name=ld_0_s_3_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 0.3333333333,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 0.375,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 0.4117647059,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_3_s_1_fc_row(
    ld_0_s_3_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_3_name,
        to_sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 3,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 2.6666666666,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 2.4285714286,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_fc_subset_desc_0(
    ld_0_s_0_s_1_fc_row: AbundancesChangeRowDescription,
    ld_0_s_0_s_3_fc_row: AbundancesChangeRowDescription,
    ld_0_s_1_s_0_fc_row: AbundancesChangeRowDescription,
    ld_0_s_1_s_3_fc_row: AbundancesChangeRowDescription,
    ld_0_s_3_s_0_fc_row: AbundancesChangeRowDescription,
    ld_0_s_3_s_1_fc_row: AbundancesChangeRowDescription,
) -> DatasetAbundancesChangeDescription:
    return DatasetAbundancesChangeDescription(
        changes=[
            ld_0_s_0_s_1_fc_row,
            ld_0_s_0_s_3_fc_row,
            ld_0_s_1_s_0_fc_row,
            ld_0_s_1_s_3_fc_row,
            ld_0_s_3_s_0_fc_row,
            ld_0_s_3_s_1_fc_row,
        ]
    )


@pytest.fixture(scope="session")
def ld_0_fc_subset_df_0(
    ld_0_fc_subset_desc_0: DatasetAbundancesChangeDescription,
) -> pd.DataFrame:
    return ld_0_fc_subset_desc_0.to_df()


@pytest.fixture(scope="session")
def ld_0_fc_subset_abundances_df_0(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_3_abundance_row: AbundanceRowDescription,
    ld_0_lipids: pd.Index,
) -> pd.DataFrame:
    return DatasetAbundancesDescription(
        lipids=ld_0_lipids,
        row_descriptions=[
            ld_0_s_0_abundance_row,
            ld_0_s_1_abundance_row,
            ld_0_s_3_abundance_row,
        ],
    ).to_df()


# *** LOG2FC ------------------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_s_0_s_1_log2fc_row(
    ld_0_s_0_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_0_name,
        to_sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: -2.5849625007,
                ld_0_lipids_collection[3].original_name: -2.1154772174,
                ld_0_lipids_collection[4].original_name: -1.8073549221,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_1_s_0_log2fc_row(
    ld_0_s_1_name: str,
    ld_0_s_0_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_1_name,
        to_sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 2.5849625007,
                ld_0_lipids_collection[3].original_name: 2.1154772174,
                ld_0_lipids_collection[4].original_name: 1.8073549221,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_0_s_3_log2fc_row(
    ld_0_s_0_name: str,
    ld_0_s_3_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_0_name,
        to_sample_name=ld_0_s_3_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: -4.9541963104,
                ld_0_lipids_collection[2].original_name: -4,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: -3.0874628413,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_3_s_0_log2fc_row(
    ld_0_s_3_name: str,
    ld_0_s_0_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_3_name,
        to_sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: np.nan,
                ld_0_lipids_collection[1].original_name: 4.9541963104,
                ld_0_lipids_collection[2].original_name: 4,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 3.0874628413,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_1_s_3_log2fc_row(
    ld_0_s_1_name: str,
    ld_0_s_3_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_1_name,
        to_sample_name=ld_0_s_3_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: -1.5849625007,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: -1.4150374993,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: -1.2801079192,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_s_3_s_1_log2fc_row(
    ld_0_s_3_name: str,
    ld_0_s_1_name: str,
    ld_0_lipids_collection: LipidCollection,
) -> AbundancesChangeRowDescription:
    return AbundancesChangeRowDescription(
        from_sample_name=ld_0_s_3_name,
        to_sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipids_collection[0].original_name: 1.5849625007,
                ld_0_lipids_collection[1].original_name: np.nan,
                ld_0_lipids_collection[2].original_name: 1.4150374993,
                ld_0_lipids_collection[3].original_name: np.nan,
                ld_0_lipids_collection[4].original_name: 1.2801079192,
            }
        ),
    )


@pytest.fixture(scope="session")
def ld_0_log2fc_subset_desc_0(
    ld_0_s_0_s_1_log2fc_row: AbundancesChangeRowDescription,
    ld_0_s_0_s_3_log2fc_row: AbundancesChangeRowDescription,
    ld_0_s_1_s_0_log2fc_row: AbundancesChangeRowDescription,
    ld_0_s_1_s_3_log2fc_row: AbundancesChangeRowDescription,
    ld_0_s_3_s_0_log2fc_row: AbundancesChangeRowDescription,
    ld_0_s_3_s_1_log2fc_row: AbundancesChangeRowDescription,
) -> DatasetAbundancesChangeDescription:
    return DatasetAbundancesChangeDescription(
        changes=[
            ld_0_s_0_s_1_log2fc_row,
            ld_0_s_0_s_3_log2fc_row,
            ld_0_s_1_s_0_log2fc_row,
            ld_0_s_1_s_3_log2fc_row,
            ld_0_s_3_s_0_log2fc_row,
            ld_0_s_3_s_1_log2fc_row,
        ]
    )


@pytest.fixture(scope="session")
def ld_0_log2fc_subset_df_0(
    ld_0_log2fc_subset_desc_0: DatasetAbundancesChangeDescription,
) -> pd.DataFrame:
    return ld_0_log2fc_subset_desc_0.to_df()


@pytest.fixture(scope="session")
def ld_0_log2fc_subset_abundances_df_0(
    ld_0_s_0_abundance_row: AbundanceRowDescription,
    ld_0_s_1_abundance_row: AbundanceRowDescription,
    ld_0_s_3_abundance_row: AbundanceRowDescription,
    ld_0_lipids: pd.Index,
) -> pd.DataFrame:
    return DatasetAbundancesDescription(
        lipids=ld_0_lipids,
        row_descriptions=[
            ld_0_s_0_abundance_row,
            ld_0_s_1_abundance_row,
            ld_0_s_3_abundance_row,
        ],
    ).to_df()


# ** ABUNDANCES CHANGES STORAGE -----------------------------------------------


@pytest.fixture(scope="session")
def ld_0_abundance_change_storage_desc(
    ld_0_lipidome_sample_names: pd.Index,
    ld_0_lipids: pd.Index,
    ld_0_differences_subset_desc_0: DatasetAbundancesChangeDescription,
    ld_0_fc_subset_desc_0: DatasetAbundancesChangeDescription,
    ld_0_log2fc_subset_desc_0: DatasetAbundancesChangeDescription,
) -> AbundanceChangeStorageDescription:
    return AbundanceChangeStorageDescription(
        lipidomes=ld_0_lipidome_sample_names,
        lipids=ld_0_lipids,
        differences_desc=ld_0_differences_subset_desc_0,
        fc_desc=ld_0_fc_subset_desc_0,
        log2fc_desc=ld_0_log2fc_subset_desc_0,
    )


@pytest.fixture(scope="session")
def ld_0_abundance_change_storage(
    ld_0_abundance_change_storage_desc: AbundanceChangeStorageDescription,
) -> AbundanceChangeStorage:
    return ld_0_abundance_change_storage_desc.to_storage()


# * LIPIDOME FEATURES ---------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_lipidome_feature_names() -> list[str]:
    return ["feature_0", "feature_1", "feature_2", "feature_3", "feature_4"]


@pytest.fixture(scope="session")
def ld_0_s_0_features_row(
    ld_0_s_0_name: str,
    ld_0_lipidome_feature_names: list[str],
) -> LipidomeFeaturesRowDescription:
    return LipidomeFeaturesRowDescription(
        sample_name=ld_0_s_0_name,
        series=pd.Series(
            {
                ld_0_lipidome_feature_names[0]: np.nan,
                ld_0_lipidome_feature_names[1]: "s_0_feature_1_value",
                ld_0_lipidome_feature_names[2]: "s_0_feature_2_value",
                ld_0_lipidome_feature_names[3]: "s_0_feature_3_value",
                ld_0_lipidome_feature_names[4]: 0,
            }
        ),
        string=f"{ld_0_s_0_name},nan,s_0_feature_1_value,s_0_feature_2_value,s_0_feature_3_value,0",  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_s_1_features_row(
    ld_0_s_1_name: str,
    ld_0_lipidome_feature_names: list[str],
) -> LipidomeFeaturesRowDescription:
    return LipidomeFeaturesRowDescription(
        sample_name=ld_0_s_1_name,
        series=pd.Series(
            {
                ld_0_lipidome_feature_names[0]: "s_1_feature_0_value",
                ld_0_lipidome_feature_names[1]: np.nan,
                ld_0_lipidome_feature_names[2]: "s_1_feature_2_value",
                ld_0_lipidome_feature_names[3]: "s_1_feature_3_value",
                ld_0_lipidome_feature_names[4]: 1,
            }
        ),
        string=f"{ld_0_s_1_name},s_1_feature_0_value,nan,s_1_feature_2_value,s_1_feature_3_value,1",  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_s_2_features_row(
    ld_0_s_2_name: str,
    ld_0_lipidome_feature_names: list[str],
) -> LipidomeFeaturesRowDescription:
    return LipidomeFeaturesRowDescription(
        sample_name=ld_0_s_2_name,
        series=pd.Series(
            {
                ld_0_lipidome_feature_names[0]: "s_2_feature_0_value",
                ld_0_lipidome_feature_names[1]: "s_2_feature_1_value",
                ld_0_lipidome_feature_names[2]: np.nan,
                ld_0_lipidome_feature_names[3]: "s_2_feature_3_value",
                ld_0_lipidome_feature_names[4]: 2,
            }
        ),
        string=f"{ld_0_s_2_name},s_2_feature_0_value,s_2_feature_1_value,nan,s_2_feature_3_value,2",  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_s_3_features_row(
    ld_0_s_3_name: str,
    ld_0_lipidome_feature_names: list[str],
) -> LipidomeFeaturesRowDescription:
    return LipidomeFeaturesRowDescription(
        sample_name=ld_0_s_3_name,
        series=pd.Series(
            {
                ld_0_lipidome_feature_names[0]: "s_3_feature_0_value",
                ld_0_lipidome_feature_names[1]: "s_3_feature_1_value",
                ld_0_lipidome_feature_names[2]: "s_3_feature_2_value",
                ld_0_lipidome_feature_names[3]: np.nan,
                ld_0_lipidome_feature_names[4]: 3,
            }
        ),
        string=f"{ld_0_s_3_name},s_3_feature_0_value,s_3_feature_1_value,s_3_feature_2_value,nan,3",  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_s_4_features_row(
    ld_0_s_4_name: str,
    ld_0_lipidome_feature_names: list[str],
) -> LipidomeFeaturesRowDescription:
    return LipidomeFeaturesRowDescription(
        sample_name=ld_0_s_4_name,
        series=pd.Series(
            {
                ld_0_lipidome_feature_names[0]: "s_4_feature_0_value",
                ld_0_lipidome_feature_names[1]: "s_4_feature_1_value",
                ld_0_lipidome_feature_names[2]: "s_4_feature_2_value",
                ld_0_lipidome_feature_names[3]: "s_4_feature_3_value",
                ld_0_lipidome_feature_names[4]: np.nan,
            }
        ),
        string=f"{ld_0_s_4_name},s_4_feature_0_value,s_4_feature_1_value,s_4_feature_2_value,s_4_feature_3_value,nan",  # noqa E501
    )


@pytest.fixture(scope="session")
def ld_0_lipidome_features_desc(
    ld_0_s_0_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_1_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_2_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_3_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_4_features_row: LipidomeFeaturesRowDescription,
) -> DatasetLipidomeFeaturesDescription:
    return DatasetLipidomeFeaturesDescription(
        features=[
            ld_0_s_0_features_row,
            ld_0_s_1_features_row,
            ld_0_s_2_features_row,
            ld_0_s_3_features_row,
            ld_0_s_4_features_row,
        ]
    )


@pytest.fixture(scope="session")
def ld_0_lipidome_features_df(
    ld_0_lipidome_features_desc: DatasetLipidomeFeaturesDescription,
) -> pd.DataFrame:
    return ld_0_lipidome_features_desc.to_df()


@pytest.fixture(scope="session")
def ld_0_lipidome_features(
    ld_0_lipidome_features_df: pd.DataFrame,
) -> LipidomeFeatures:
    return LipidomeFeatures(ld_0_lipidome_features_df)


@pytest.fixture(scope="session")
def ld_0_lipidome_features_str(
    ld_0_lipidome_feature_names: list[str],
    ld_0_lipidome_features_desc: DatasetLipidomeFeaturesDescription,
) -> str:
    header: str = "INDEX," + ",".join(ld_0_lipidome_feature_names)
    features_str: str = (
        header
        + "\n"
        + "\n".join([lf.string for lf in ld_0_lipidome_features_desc.features])
    )

    return features_str


@pytest.fixture(scope="function")
def ld_0_lipidome_features_str_io(
    ld_0_lipidome_features_str: str,
) -> StringIO:
    return StringIO(ld_0_lipidome_features_str)


@pytest.fixture(scope="session")
def ld_0_lipidome_features_tmp_file_path(
    tmp_path_factory: TempPathFactory,
    ld_0_lipidome_features_str: str,
) -> Path:
    tmp_file_path = tmp_path_factory.mktemp("lipidomes") / "ld_1_features.csv"

    with open(tmp_file_path, "w") as f:
        f.write(ld_0_lipidome_features_str)

    return tmp_file_path


# ** FEATURES AGGREGATION ----------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_lipidome_features_get_aggregation_data_0(
    ld_0_s_0_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_1_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_2_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_3_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_4_features_row: LipidomeFeaturesRowDescription,
    ld_0_lipidome_feature_names: list[str],
) -> LipidomeFeaturesAggregationTestData:
    lipidome_indeces: list[pd.Index] = [
        pd.Index(
            [
                ld_0_s_0_features_row.sample_name,
                ld_0_s_1_features_row.sample_name,
            ]
        ),
        pd.Index(
            [
                ld_0_s_2_features_row.sample_name,
                ld_0_s_3_features_row.sample_name,
            ]
        ),
        pd.Index(
            [
                ld_0_s_4_features_row.sample_name,
                ld_0_s_0_features_row.sample_name,
            ]
        ),
    ]

    lipidome_features: pd.DataFrame = pd.DataFrame(
        [
            {
                "INDEX": "agg_0",
                ld_0_lipidome_feature_names[0]: "nan | s_1_feature_0_value",
                ld_0_lipidome_feature_names[1]: "s_0_feature_1_value | nan",
                ld_0_lipidome_feature_names[
                    2
                ]: "s_0_feature_2_value | s_1_feature_2_value",
                ld_0_lipidome_feature_names[
                    3
                ]: "s_0_feature_3_value | s_1_feature_3_value",
                ld_0_lipidome_feature_names[4]: "0.0 | 1.0",
            },
            {
                "INDEX": "agg_1",
                ld_0_lipidome_feature_names[
                    0
                ]: "s_2_feature_0_value | s_3_feature_0_value",
                ld_0_lipidome_feature_names[
                    1
                ]: "s_2_feature_1_value | s_3_feature_1_value",
                ld_0_lipidome_feature_names[2]: "nan | s_3_feature_2_value",
                ld_0_lipidome_feature_names[3]: "s_2_feature_3_value | nan",
                ld_0_lipidome_feature_names[4]: "2.0 | 3.0",
            },
            {
                "INDEX": "agg_2",
                ld_0_lipidome_feature_names[0]: "s_4_feature_0_value | nan",
                ld_0_lipidome_feature_names[
                    1
                ]: "s_4_feature_1_value | s_0_feature_1_value",
                ld_0_lipidome_feature_names[
                    2
                ]: "s_4_feature_2_value | s_0_feature_2_value",
                ld_0_lipidome_feature_names[
                    3
                ]: "s_4_feature_3_value | s_0_feature_3_value",
                ld_0_lipidome_feature_names[4]: "nan | 0.0",
            },
        ],
    ).set_index("INDEX")

    group_names: list[str] = ["agg_0", "agg_1", "agg_2"]

    return LipidomeFeaturesAggregationTestData(
        lipidome_indeces=lipidome_indeces,
        group_names=group_names,
        lipidome_features=LipidomeFeatures(lipidome_features),
    )


@pytest.fixture(scope="session")
def ld_0_lipidome_features_add_subset_aggregation_data_0(
    ld_0_lipidome_features_get_aggregation_data_0: LipidomeFeaturesAggregationTestData,  # noqa E501
    ld_0_lipidome_features_df: pd.DataFrame,
) -> LipidomeFeaturesAggregationTestData:
    features_df: pd.DataFrame = pd.concat(
        [
            ld_0_lipidome_features_df,
            ld_0_lipidome_features_get_aggregation_data_0.lipidome_features.df,
        ]
    )

    return LipidomeFeaturesAggregationTestData(
        lipidome_indeces=ld_0_lipidome_features_get_aggregation_data_0.lipidome_indeces,  # noqa E501
        group_names=ld_0_lipidome_features_get_aggregation_data_0.group_names,
        lipidome_features=LipidomeFeatures(features_df),
    )


@pytest.fixture(scope="session")
def ld_0_lipidome_features_add_feature_data_0(
    ld_0_s_0_features_row: LipidomeFeaturesRowDescription,
    ld_0_s_1_features_row: LipidomeFeaturesRowDescription,
) -> LipidomeFeaturesAddFeatureTestData:
    features_description: DatasetLipidomeFeaturesDescription = (
        DatasetLipidomeFeaturesDescription(
            [
                ld_0_s_0_features_row,
                ld_0_s_1_features_row,
            ]
        )
    )
    lipidome_features: LipidomeFeatures = LipidomeFeatures(
        features_description.to_df()
    )

    updated_features_description: DatasetLipidomeFeaturesDescription = (
        DatasetLipidomeFeaturesDescription(
            [
                LipidomeFeaturesRowDescription(
                    sample_name=ld_0_s_0_features_row.sample_name,
                    series=pd.concat(
                        [
                            ld_0_s_0_features_row.series,
                            pd.Series(
                                {"new_feature": "s_0_new_feature_value"}
                            ),
                        ]
                    ),
                    string=ld_0_s_0_features_row.string
                    + ",s_0_new_feature_value",  # noqa E501
                ),
                LipidomeFeaturesRowDescription(
                    sample_name=ld_0_s_1_features_row.sample_name,
                    series=pd.concat(
                        [
                            ld_0_s_1_features_row.series,
                            pd.Series(
                                {"new_feature": "s_1_new_feature_value"}
                            ),
                        ]
                    ),
                    string=ld_0_s_1_features_row.string
                    + ",s_1_new_feature_value",  # noqa E501
                ),
            ]
        )
    )
    updated_lipidome_features: LipidomeFeatures = LipidomeFeatures(
        updated_features_description.to_df()
    )

    feature_values: pd.Series = pd.Series(
        ["s_0_new_feature_value", "s_1_new_feature_value"],
        index=lipidome_features.df.index,
    )

    return LipidomeFeaturesAddFeatureTestData(
        lipidome_features=lipidome_features,
        updated_lipidome_features=updated_lipidome_features,
        feature_name="new_feature",
        feature_values=feature_values,
        overwrite=False,
    )


# * LIPID FEATURES -----------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_lipid_features_empty_df(ld_0_lipids: pd.Index) -> pd.DataFrame:
    return pd.DataFrame(index=ld_0_lipids)


@pytest.fixture(scope="session")
def ld_0_lipid_features_empty(ld_0_lipids: pd.Index) -> LipidFeatures:
    return LipidFeatures.empty_from_lipids(ld_0_lipids)


# * LIPIDOME DATASET ---------------------------------------------------------


@pytest.fixture(scope="session")
def ld_0_desc(
    ld_0_abundances_desc: DatasetAbundancesDescription,
    ld_0_abundance_change_storage_desc: AbundanceChangeStorageDescription,
    ld_0_features_desc: DatasetLipidomeFeaturesDescription,
) -> LipidomeDatasetDescription:
    return LipidomeDatasetDescription(
        name="ld_0",
        abundances=ld_0_abundances_desc,
        abundance_change_storage=ld_0_abundance_change_storage_desc,
        lipidome_features=ld_0_features_desc,
    )
