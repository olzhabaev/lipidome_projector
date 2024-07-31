"""Module concerning the registration of callbacks."""

import logging

from lipidome_projector.callbacks.app_settings_callback_definition import (  # noqa: E501
    reg_app_settings_callbacks_python,
)

from lipidome_projector.callbacks.data_operation_callback_definition import (  # noqa: E501
    reg_data_operation_callbacks_python,
)
from lipidome_projector.callbacks.default_dataset_callback_definition import (  # noqa: E501
    reg_default_dataset_callbacks_python,
)
from lipidome_projector.callbacks.graph_settings_callback_definition import (  # noqa: E501
    reg_graph_settings_callbacks_python,
)
from lipidome_projector.callbacks.grid_callback_definition import (
    reg_grid_callbacks_python,
)
from lipidome_projector.callbacks.upload_callback_definition import (
    reg_upload_callbacks_python,
)
from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.default_dataset_processing import (
    DefaultLipidomeData,
)
from lipidome_projector.front_end.front_end_coordination import FrontEnd


logger: logging.Logger = logging.getLogger(__name__)


def reg_callbacks(
    front_end: FrontEnd,
    database: BaseDB,
    default_lipidome_data: DefaultLipidomeData,
    col_names: ColNames,
) -> None:
    logger.info("Register callbacks.")

    reg_app_settings_callbacks_python(front_end)
    reg_default_dataset_callbacks_python(front_end, default_lipidome_data)
    reg_upload_callbacks_python(front_end, database, col_names)
    reg_grid_callbacks_python(front_end, col_names)
    reg_graph_settings_callbacks_python(front_end, col_names)
    reg_data_operation_callbacks_python(front_end, col_names)
