"""Module concerning the standardization of lipid structures."""

import logging

from typing import Literal

import pandas as pd

from rdkit.Chem.MolStandardize import rdMolStandardize  # type: ignore
from rdkit import RDLogger


logger: logging.Logger = logging.getLogger(__name__)


def uncharge_mols(
    mols: pd.Series,
    nan_handling: Literal["drop", "keepnan", "raise"] = "keepnan",
) -> pd.Series:
    """Uncharge charged molecules.
    :param mols: Series of mol objects.
    :param nan_handling: How to handle NaN values. If "drop",
        NaN values are dropped. If "keepnan", NaN values are
        kept. If "raise", an exception is raised if NaN values
        are present.
    :return: Series of uncharged mol objects.
    """
    if nan_handling == "drop":
        mols = mols.dropna()
    elif nan_handling == "raise":
        if mols.isna().any():
            raise ValueError("NaN values are present.")

    # Necessary, as uncharge() call produces a log message.
    RDLogger.DisableLog("rdApp.info")  # type: ignore

    uncharger: rdMolStandardize.Uncharger = rdMolStandardize.Uncharger()

    mols_uc: pd.Series = mols.apply(
        lambda mol: uncharger.uncharge(mol) if pd.notna(mol) else mol
    )

    RDLogger.EnableLog("rdApp.info")  # type: ignore

    return mols_uc
