"""Module concerning fixtures."""

import logging

from tests.test_lipid_data_processing.fixtures.combined_db_fixtures import *  # noqa: F401 F403 E501 # type: ignore
from tests.test_lipid_data_processing.fixtures.full_lipid_group_fixtures import *  # noqa: F401 F403 E501 # type: ignore
from tests.test_lipid_data_processing.fixtures.lipidome_fixtures import *  # noqa: F401 F403 E501 # type: ignore
from tests.test_lipid_data_processing.fixtures.lmsd_fixtures import *  # noqa: F401, F403, E501  # type: ignore
from tests.test_lipid_data_processing.fixtures.notation_fixtures import *  # noqa: F401 F403 E501 # type: ignore
from tests.test_lipid_data_processing.fixtures.sl_fixtures import *  # noqa: F401, F403, E501  # type: ignore
from tests.test_lipid_data_processing.fixtures.structure_fixtures import *  # noqa: F401 F403 E501 # type: ignore

logger: logging.Logger = logging.getLogger(__name__)
