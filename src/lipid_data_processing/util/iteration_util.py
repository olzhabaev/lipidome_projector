"""Module concerning iteration utilities."""

import logging

from collections.abc import Generator

import numpy as np
import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


def gen_pd_chunks[
    PDObjType: (pd.DataFrame, pd.Series)
](pd_obj: PDObjType, num_chunks: int) -> Generator[PDObjType, None, None]:
    if num_chunks > len(pd_obj):
        raise ValueError(
            f"Number of chunks ({num_chunks}) must be less than or "
            f"equal to the length of the pandas object ({len(pd_obj)})."
        )

    index_split: list[np.ndarray] = np.array_split(pd_obj.index, num_chunks)

    return (pd_obj.loc[chunk_index] for chunk_index in index_split)
