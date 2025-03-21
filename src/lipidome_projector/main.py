"""Lipidome projector entry point."""

import logging

from importlib.resources import files
from pathlib import Path

from dash import Dash
from dash.html import Div

from lipidome_projector.callbacks.callback_registration import (
    reg_callbacks,
)
from lipidome_projector.database.base_db import BaseDB
from lipidome_projector.database.db_handling import create_database
from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.default_dataset_processing import (
    DefaultLipidomeData,
)


logger: logging.Logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    logging.basicConfig(level=logging.DEBUG)


def _load_db(path: Path) -> BaseDB:
    database: BaseDB = create_database(path)

    return database


def _create_app(layout: Div) -> Dash:
    app: Dash = Dash(
        __name__,
        assets_ignore="SLATE.css",
        prevent_initial_callbacks=True,
        title="Lipidome Projector",
    )

    app.layout = layout

    return app


def main() -> None:
    """Start the lipidome projector application server."""

    _setup_logging()

    logger.info("Initialize.")

    database: BaseDB = _load_db(
        files("lipidome_projector.configuration").joinpath(
            "database_config.toml"
        )
    )

    col_names: ColNames = ColNames()

    default_lipidome_data: DefaultLipidomeData = (
        DefaultLipidomeData.from_config_file(
            files("lipidome_projector.configuration").joinpath(
                "default_lipidome_data_config.toml"
            ),
            database,
            col_names,
        )
    )

    front_end: FrontEnd = FrontEnd()

    reg_callbacks(
        front_end=front_end,
        database=database,
        default_lipidome_data=default_lipidome_data,
        col_names=col_names,
    )

    logger.info("Run server.")

    layout: Div = front_end.gen_layout(
        default_lipidome_data._dataset_descriptions, col_names
    )

    app: Dash = _create_app(layout)

    # debug: bool = True
    debug: bool = False
    # use_reloader: bool = True
    use_reloader: bool = False

    app.run(
        debug=debug, host="0.0.0.0", port=8050, use_reloader=use_reloader
    )


if __name__ == "__main__":
    main()
