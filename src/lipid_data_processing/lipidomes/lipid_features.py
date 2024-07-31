"""Module concerning lipid features."""


import logging

from typing import Self

import pandas as pd

from lipid_data_processing.lipidomes.base_df_wrapper import BaseDfWrapper


logger: logging.Logger = logging.getLogger(__name__)


class LipidFeatures(BaseDfWrapper):
    def __init__(
        self,
        df: pd.DataFrame,
        validate: bool = True,
    ):
        super().__init__(df, validate=validate)

    @classmethod
    def empty_from_lipids(
        cls, lipids: pd.Index, validate: bool = True
    ) -> Self:
        df: pd.DataFrame = pd.DataFrame(index=lipids)

        return cls(df, validate=validate)

    @property
    def lipids(self) -> pd.Index:
        return self.df.index

    def get_subset(
        self,
        lipids: pd.Index | None = None,
        features: pd.Index | None = None,
        validate: bool = True,
    ) -> Self:
        subset_df: pd.DataFrame = self.get_subset_df(
            index=lipids, columns=features, validate=validate
        )

        return type(self)(df=subset_df, validate=False)
