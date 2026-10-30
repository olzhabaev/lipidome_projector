"""Module concerning fixtures."""

import logging

from pathlib import Path

import pytest

from tests.test_embedding_visualization.case_1_fixtures import *  # noqa: F401, F403, E501
from tests.test_embedding_visualization.scatter_data_fixtures import *  # noqa: F401, F403, E501

logger: logging.Logger = logging.getLogger(__name__)


# WRITING ---------------------------------------------------------------------


@pytest.fixture(scope="session")
def base_dir() -> Path:
    base_dir: Path = Path("tests/output")
    base_dir.mkdir(exist_ok=True)

    gitignore_path = base_dir / ".gitignore"
    with gitignore_path.open("w") as gitignore_file:
        gitignore_file.write("*\n")

    return base_dir
