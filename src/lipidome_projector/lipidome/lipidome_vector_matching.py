"""Module concerning the matching of vectors to lipidomes."""

import logging

from typing import cast

import numpy as np
import pandas as pd

from scipy.spatial.distance import cdist

from lipid_data_processing.lipidomes.lipidome_dataset import LipidomeDataset
from lipid_data_processing.notation.matching import (
    ConstraintsDataset,
    MatchingResults,
    perform_constrained_match,
)
from lipid_data_processing.notation.matching_summary import MatchingSummary
from lipid_data_processing.notation.parsing import (
    ParsedDataset,
    parse_name_series,
)


logger: logging.Logger = logging.getLogger(__name__)

# TODO: Understand, simplify, make more clear.


def perf_vector_matching(
    lipidome_ds: LipidomeDataset,
    constraints_ds: ConstraintsDataset,
    database_matching_ds: ParsedDataset,
    isomer_vectors_df: pd.DataFrame,
    isomer_smiles: pd.Series,
    lipid_col_name: str,
) -> tuple[LipidomeDataset, MatchingSummary]:
    """Create a lipidome dataset with lipid vectors.
    :param lipidome_ds: Lipidome dataset.
    :param constraints_ds: Constraints dataset.
    :param database_matching_ds: Database matching dataset.
    :param isomer_vectors_df: Dataframe containing database
        isomer vectors.
    :param isomer_smiles: Series containing database isomer SMILES.
    :param lipid_col_name: Name of the lipid column.
    :returns: Vector lipidome dataset with lipid vectors as lipid
        features and the matching summary.
    """
    lipidome_matching_ds: ParsedDataset = _gen_matching_ds(lipidome_ds)

    matching_results: MatchingResults = perform_constrained_match(
        lipidome_matching_ds,
        database_matching_ds,
        constraints_ds,
    )

    lipid_features_df: pd.DataFrame = _gen_lipid_features_df(
        lipidome_ds=lipidome_ds,
        matching_results=matching_results,
        database_matching_ds=database_matching_ds,
        isomer_vectors_df=isomer_vectors_df,
        isomer_smiles=isomer_smiles,
        lipid_col_name=lipid_col_name,
    )

    filtered_abundance_df: pd.DataFrame = lipidome_ds.abundance_df[
        lipid_features_df.index.to_list()
    ]

    vec_lipidome_ds: LipidomeDataset = LipidomeDataset.from_prepared_dfs(
        name=lipidome_ds.name,
        abundance_df=filtered_abundance_df,
        lipidome_features_df=lipidome_ds.lipidome_features_df,
        lipid_features_df=lipid_features_df,
    )

    matching_summary: MatchingSummary = MatchingSummary(
        lipidome_ds.name,
        "DATABASE",
        lipidome_matching_ds,
        matching_results,
    )

    return vec_lipidome_ds, matching_summary


def _gen_matching_ds(lipidome_ds: LipidomeDataset) -> ParsedDataset:
    parsed_lipid_ds: ParsedDataset = parse_name_series(
        lipidome_ds.lipids.to_series()
    )

    lipidome_matching_ds: ParsedDataset = ParsedDataset(parsed_lipid_ds.df)

    return lipidome_matching_ds


def _gen_lipid_features_df(
    lipidome_ds: LipidomeDataset,
    matching_results: MatchingResults,
    database_matching_ds: ParsedDataset,
    isomer_vectors_df: pd.DataFrame,
    isomer_smiles: pd.Series,
    lipid_col_name: str,
) -> pd.DataFrame:
    lipid_features_df: pd.DataFrame = _gen_vectors_features_df(
        matching_results=matching_results,
        database_matching_ds=database_matching_ds,
        isomer_vectors_df=isomer_vectors_df,
        lipid_col_name=lipid_col_name,
        isomer_smiles=isomer_smiles,
    )

    lipid_features_df = lipid_features_df.merge(
        lipidome_ds.lipid_features_df,
        how="left",
        left_index=True,
        right_index=True,
        validate="1:1",
    )

    lipid_features_df.index.name = lipid_col_name

    return lipid_features_df


def _gen_vectors_features_df(
    matching_results: MatchingResults,
    database_matching_ds: ParsedDataset,
    isomer_vectors_df: pd.DataFrame,
    isomer_smiles: pd.Series,
    lipid_col_name: str,
) -> pd.DataFrame:
    isomer_lipid_map: pd.Series = (
        matching_results.constrained_matches_info.dataframe[
            [
                matching_results.constrained_matches_info.to_match_original_name_col_name,  # noqa: E501
                matching_results.constrained_matches_info.match_to_index_col_name,  # noqa: E501
            ]
        ]
        .set_index(
            matching_results.constrained_matches_info.match_to_index_col_name
        )[
            matching_results.constrained_matches_info.to_match_original_name_col_name  # noqa: E501
        ]
        .rename(lipid_col_name)
    )

    lipid_features_df: pd.DataFrame = _merge_and_aggregate(
        isomer_lipid_map=isomer_lipid_map,
        isomer_vectors_df=isomer_vectors_df,
        database_matching_ds=database_matching_ds,
        isomer_smiles=isomer_smiles,
        lipid_col_name=lipid_col_name,
    )

    return lipid_features_df


def _merge_and_aggregate(
    isomer_lipid_map: pd.Series,
    isomer_vectors_df: pd.DataFrame,
    database_matching_ds: ParsedDataset,
    isomer_smiles: pd.Series,
    lipid_col_name: str,
    drop_duplicate_isomer_vectors: bool = True,
) -> pd.DataFrame:
    isomer_features_df: pd.DataFrame = _gen_isomer_features_df(
        isomer_lipid_map=isomer_lipid_map,
        isomer_vectors_df=isomer_vectors_df,
        database_matching_ds=database_matching_ds,
        isomer_smiles=isomer_smiles,
        drop_duplicate_isomer_vectors=drop_duplicate_isomer_vectors,
    )

    _chk_isomer_features_df_missing_vectors(
        isomer_features_df=isomer_features_df,
        isomer_vectors_df=isomer_vectors_df,
    )

    lipid_features_df: pd.DataFrame = isomer_features_df.groupby(
        lipid_col_name
    ).apply(
        lambda group: _process_lipid_feature_group(
            group=group,
            vec_col_names_2d=isomer_vectors_df.columns[0:2].to_list(),
            vec_col_names_3d=isomer_vectors_df.columns[2:].to_list(),
            category_col_name=database_matching_ds.col_names.category,
            class_col_name=database_matching_ds.col_names.class_,
            smiles_col_name=cast(str, isomer_smiles.name),
        )
    )

    return lipid_features_df


def _gen_isomer_features_df(
    isomer_lipid_map: pd.Series,
    isomer_vectors_df: pd.DataFrame,
    database_matching_ds: ParsedDataset,
    isomer_smiles: pd.Series,
    drop_duplicate_isomer_vectors: bool = True,
) -> pd.DataFrame:
    isomer_features_df: pd.DataFrame = (
        isomer_lipid_map.to_frame()
        .merge(
            isomer_vectors_df,
            how="left",
            left_index=True,
            right_index=True,
            validate="1:1",
        )
        .merge(
            database_matching_ds.df[
                [
                    database_matching_ds.col_names.category,
                    database_matching_ds.col_names.class_,
                ]
            ],
            how="left",
            left_index=True,
            right_index=True,
            validate="1:1",
        )
        .merge(
            isomer_smiles.to_frame(),
            how="left",
            left_index=True,
            right_index=True,
            validate="1:1",
        )
    )

    if drop_duplicate_isomer_vectors:
        isomer_features_df.drop_duplicates(
            subset=isomer_vectors_df.columns, inplace=True
        )

    return isomer_features_df


def _chk_isomer_features_df_missing_vectors(
    isomer_features_df: pd.DataFrame, isomer_vectors_df: pd.DataFrame
) -> None:
    missing_vectors: pd.Series = (
        isomer_features_df[isomer_vectors_df.columns].isna().any()
    )

    if missing_vectors.any():
        raise ValueError(f"Vectors missing for lipids: {missing_vectors}.")


def _process_lipid_feature_group(
    group: pd.DataFrame,
    vec_col_names_2d: list[str],
    vec_col_names_3d: list[str],
    category_col_name: str,
    class_col_name: str,
    smiles_col_name: str,
) -> pd.Series:
    mean_vec_2d: pd.Series = group[vec_col_names_2d].mean()
    mean_vec_3d: pd.Series = group[vec_col_names_3d].mean()

    closest_to_mean_idx_2d = np.argmin(
        cdist(group[vec_col_names_2d], mean_vec_2d.to_frame().T)
    )

    smiles_rep_2d: str = group.iloc[closest_to_mean_idx_2d][smiles_col_name]

    lipid_category: str = " | ".join(group[category_col_name].unique())
    lipid_class: str = " | ".join(group[class_col_name].unique())

    lipid_features: pd.Series = pd.Series(
        {
            category_col_name: lipid_category,
            class_col_name: lipid_class,
            smiles_col_name: smiles_rep_2d,
            **mean_vec_2d,
            **mean_vec_3d,
        }
    ).rename(str(group.name))

    return lipid_features
