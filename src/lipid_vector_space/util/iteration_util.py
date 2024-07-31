"""Module concering iteration utilities."""

import logging

from collections.abc import Callable, Generator, Hashable, Iterable
from typing import Any, Self

import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


class SeriesWrapper:
    def __init__(self, descriptors: pd.Series) -> None:
        self._series: pd.Series = descriptors

    def get_element_iter(self) -> Iterable[Any]:
        return self._series

    def get_indexed_element_iter(self) -> Iterable[tuple[Hashable, Any]]:
        return self._series.items()

    def derive(self, transformer: Callable) -> Self:
        return type(self)(self._series.apply(transformer))

    def shuffle(self) -> Self:
        return type(self)(self._series.sample(frac=1))

    def combine(self, other: Self, combinator: Callable) -> Self:
        return type(self)(self._series.combine(other.series, combinator))

    @property
    def series(self) -> pd.Series:
        return self._series


class SeriesWrapperIter:
    def __init__(self, iter: Iterable[SeriesWrapper]) -> None:
        self._iter: Iterable[SeriesWrapper] = iter

    @classmethod
    def from_series_iter(cls, series_iter: Iterable[pd.Series]) -> Self:
        return cls(SeriesWrapper(series) for series in series_iter)

    def get_element_iter(self) -> Generator[Any, None, None]:
        return (
            element
            for series_wrapper in self._iter
            for element in series_wrapper.get_element_iter()
        )

    def get_indexed_element_iter(self) -> Iterable[tuple[Hashable, Any]]:
        return (
            index_element_tuple
            for series_wrapper in self._iter
            for index_element_tuple in series_wrapper.get_indexed_element_iter()  # noqa E501
        )

    def get_series_iter(self) -> Iterable[SeriesWrapper]:
        return self._iter

    def to_series_iter(self) -> Generator[pd.Series, None, None]:
        return (series_wrapper.series for series_wrapper in self._iter)

    def derive(self, transformer: Callable) -> Self:
        return type(self)(
            series_wrapper.derive(transformer) for series_wrapper in self._iter
        )

    def shuffle_each(self) -> Self:
        return type(self)(
            series_wrapper.shuffle() for series_wrapper in self._iter
        )

    def combine(self, other: Self, combinator: Callable) -> Self:
        return type(self)(
            series_wrapper.combine(other_series_wrapper, combinator)
            for series_wrapper, other_series_wrapper in zip(
                self.get_series_iter(), other.get_series_iter()
            )
        )
