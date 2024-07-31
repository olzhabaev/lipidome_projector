"""Module concerning the IO of structure data."""

import logging

from pathlib import Path

import pandas as pd

from rdkit import Chem
from rdkit.Chem import Mol


logger: logging.Logger = logging.getLogger(__name__)


def sdf_to_df(path: Path, add_rdkit_data: bool) -> pd.DataFrame:
    failure_index: list[int] = []
    records: list[dict[str, Mol | str]] = []
    mol_supplier: Chem.SDMolSupplier = Chem.SDMolSupplier(str(path))

    for i, mol in enumerate(mol_supplier):
        if mol is None:
            failure_index.append(i)
        else:
            records.append(_gen_mol_record_dict(mol, add_rdkit_data))

    if failure_index:
        logger.warn(
            "Some records could not be read from the SDF file. The following"
            "indexes could not be read: {}".format(failure_index)
        )

    df: pd.DataFrame = pd.DataFrame.from_records(records)

    return df


def _gen_mol_record_dict(mol: Mol, add_rdkit_data: bool) -> dict[str, str]:
    record: dict[str, str] = {
        name: mol.GetProp(name) for name in mol.GetPropNames()
    }

    if add_rdkit_data:
        record["rdkit_mol"] = mol
        record["rdkit_smiles"] = Chem.MolToSmiles(
            mol, isomericSmiles=True, canonical=True
        )

    return record
