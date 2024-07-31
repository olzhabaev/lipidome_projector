"""IO utility module."""

import logging

from pathlib import Path
from typing import Generator, Iterable

import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


class SeriesFromFilesGenerator:
    def __init__(self, paths: list[Path]) -> None:
        self._paths: list[Path] = paths
        self._chk_paths()

    def __iter__(self) -> Generator[pd.Series, None, None]:
        return (self._read_series(path) for path in self._paths)

    def _chk_paths(self) -> None:
        for path in self._paths:
            chk_file_exists(path)

    def _read_series(self, path: Path) -> pd.Series:
        logger.info(f"Read series from '{path}'.")
        return pd.read_pickle(path)


def write_series_iter_to_files(
    series_iter: Iterable[pd.Series], paths: Iterable[Path]
) -> None:
    """Write iterable of series to files.
    :param series_iter: Iterable of series to write.
    :param paths: Paths to write the series to.
    """
    for series, path in zip(series_iter, paths):
        logger.info(f"Write series to '{path}'.")
        series.to_pickle(path)


def chk_file_exists(file_path: Path) -> None:
    """Check if a file exists.
    :param file_path: Path to the file to check.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File {file_path} does not exist.")


def chk_files_exist(file_paths: list[Path]) -> None:
    """Check if files exist.
    :param file_paths: Paths to the files to check.
    """
    non_existing_files: list[Path] = [
        path for path in file_paths if not path.is_file()
    ]

    if non_existing_files:
        raise FileNotFoundError(
            f"The following files do not exist: {non_existing_files}."
        )


def chk_file_doesnt_exist(file_path: Path) -> None:
    """Check if a file does not exist.
    :param file_path: Path to the file to check.
    """
    if file_path.is_file():
        raise FileExistsError(f"File {file_path} already exists.")


def chk_files_dont_exist(file_paths: list[Path]) -> None:
    """Check if files do not exist.
    :param file_paths: Paths to the files to check.
    """
    existing_files: list[Path] = [
        path for path in file_paths if path.is_file()
    ]

    if existing_files:
        raise FileExistsError(
            f"The following files already exist: {existing_files}."
        )


def chk_dir_exists(dir_path: Path) -> None:
    """Check if a directory exists.
    :param dir_path: Path to the directory to check.
    """
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Directory {dir_path} does not exist.")


def chk_parent_dir_exists(file_path: Path) -> None:
    """Check if the parent directory of a file exists.
    :param file_path: Path to the file to check.
    """
    chk_dir_exists(file_path.parent)


def chk_parent_dirs_exist(file_paths: list[Path]) -> None:
    """Check if the parent directories of files exist.
    :param file_paths: Paths to the files to check.
    """
    paths_with_no_parent: list[Path] = [
        path for path in file_paths if not path.parent.is_dir()
    ]

    if paths_with_no_parent:
        raise FileNotFoundError(
            f"The following paths have non-existing parent directories: "
            f"{paths_with_no_parent}."
        )


def add_prefix_to_filename(path: Path, prefix: str) -> Path:
    """Add a prefix to the filename of a path.
    :param path: Path to add the prefix to.
    :param prefix: Prefix to add.
    :return: Path with the prefix added.
    """
    return path.with_stem(f"{prefix}{path.stem}")


def add_suffix_to_filename(path: Path, suffix: str) -> Path:
    """Add a suffix to the filename of a path.
    :param path: Path to add the suffix to.
    :param suffix: Suffix to add.
    :return: Path with the suffix added.
    """
    return path.with_stem(f"{path.stem}{suffix}")
