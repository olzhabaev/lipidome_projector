import logging

from pathlib import Path

import pandas as pd

from lipid_data_processing.notation.parsing import ParsedDataset

logging.basicConfig(level=logging.INFO)

logger: logging.Logger = logging.getLogger(__name__)

output_dir_path: Path = Path("output")

vectors_df_2d: pd.DataFrame = pd.read_csv(
    output_dir_path / "vectors_2d.csv", index_col=0
)

vectors_df_3d: pd.DataFrame = pd.read_csv(
    output_dir_path / "vectors_3d.csv", index_col=0
)

lmsd_matching_ds: ParsedDataset = ParsedDataset.from_csv_input(
    output_dir_path / "lmsd_parsed.csv", fillna=""
)

sl_matching_ds: ParsedDataset = ParsedDataset.from_csv_input(
    output_dir_path / "sl_parsed.csv", fillna=""
)

combined_parsed_db: ParsedDataset = lmsd_matching_ds.concat_ds(sl_matching_ds)

combined_parsed_db = combined_parsed_db.get_subset(
    vectors_df_2d.index, intersection=True
)

lmsd_smiles: pd.Series = pd.read_csv(
    output_dir_path / "lmsd_smiles.csv", index_col=0
).squeeze()
sl_siles: pd.Series = pd.read_csv(
    output_dir_path / "sl_smiles.csv", index_col=0
).squeeze()

combined_smiles: pd.Series = (
    pd.concat([lmsd_smiles, sl_siles])
    .loc[combined_parsed_db.df.index]
    .rename("SMILES")
)

combined_smiles.index.name = "INDEX"

vectors_df_2d = vectors_df_2d.loc[combined_parsed_db.df.index]
vectors_df_3d = vectors_df_3d.loc[combined_parsed_db.df.index]

logger.info("Save processed data.")
combined_parsed_db.df.to_csv(output_dir_path / "database.zip")
vectors_df_2d.to_csv(output_dir_path / "vectors_2d.zip")
vectors_df_3d.to_csv(output_dir_path / "vectors_3d.zip")
combined_smiles.to_csv(output_dir_path / "smiles.zip")
