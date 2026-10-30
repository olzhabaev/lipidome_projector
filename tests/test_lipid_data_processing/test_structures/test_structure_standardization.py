import logging

import pandas as pd
import pytest

from rdkit import Chem

from lipid_data_processing.structures.structure_standardization import (
    uncharge_mols,
)


logger: logging.Logger = logging.getLogger(__name__)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_uncharge_mols(
    charged_mols: pd.Series,
    uncharged_mols_smiles: pd.Series,
) -> None:
    test_uncharged_mols: pd.Series = uncharge_mols(charged_mols)
    test_uncharged_mols_smiles: pd.Series = test_uncharged_mols.apply(
        Chem.MolToSmiles, canonical=False
    )

    pd.testing.assert_series_equal(
        uncharged_mols_smiles, test_uncharged_mols_smiles
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_uncharge_mols_nan_handling_drop(
    charged_mols: pd.Series,
    uncharged_mols_smiles: pd.Series,
) -> None:
    charged_mols_with_nan: pd.Series = charged_mols.copy()
    charged_mols_with_nan.iloc[-1] = pd.NA

    test_uncharged_mols: pd.Series = uncharge_mols(
        charged_mols_with_nan, nan_handling="drop"
    )
    test_uncharged_mols_smiles: pd.Series = test_uncharged_mols.apply(
        Chem.MolToSmiles, canonical=False
    )

    pd.testing.assert_series_equal(
        uncharged_mols_smiles.iloc[0:-1], test_uncharged_mols_smiles
    )
