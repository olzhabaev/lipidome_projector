"""Lipidome projector entry point."""

import logging

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

from dash import Dash
from dash.html import Div

from lipidome_projector.callbacks.callback_registration import (
    reg_callbacks,
)

from lipidome_projector.database.in_memory_df_db import (
    DBCfg,
    InMemoryDataFrameDB,
)
from lipidome_projector.front_end.front_end_coordination import FrontEnd
from lipidome_projector.lipidome.col_names import ColNames
from lipidome_projector.lipidome.default_dataset_processing import (
    DefaultLipidomeData,
)


logger: logging.Logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    logging.basicConfig(level=logging.DEBUG)


def _create_app(layout: Div) -> Dash:
    app: Dash = Dash(
        __name__,
        assets_ignore="SLATE.css",
        prevent_initial_callbacks=True,
        title="Lipidome Projector",
    )

    app.layout = layout

    return app


def _run(
    db_cfg_path: Path,
    db_anchor: Traversable,
    lipidome_cfg_path: Path,
    lipidome_anchor: Traversable,
    debug: bool,
) -> None:
    """Start the lipidome projector application server.
    :param db_cfg_path: Path to the database configuration file.
    :param db_anchor: Anchor for database files.
    :param lipidome_cfg_path: Path to the lipidome configuration file.
    :param lipidome_anchor: Anchor for lipidome files.
    :param debug: Debug mode.
    """

    _setup_logging()

    logger.info("Initialize.")

    database: InMemoryDataFrameDB = InMemoryDataFrameDB.from_cfg(
        DBCfg.from_cfg_file_with_anchor(db_cfg_path, db_anchor)
    )

    col_names: ColNames = ColNames()

    default_lipidome_data: DefaultLipidomeData = (
        DefaultLipidomeData.from_cfg_file_with_anchor(
            lipidome_cfg_path,
            lipidome_anchor,
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

    app.run(debug=debug, host="0.0.0.0", port=8050, use_reloader=False)


def main() -> None:
    _run(
        db_cfg_path=Path(
            str(
                files("lipidome_projector").joinpath(
                    "configuration/database_config.toml"
                )
            )
        ),
        db_anchor=files("lipidome_projector"),
        lipidome_cfg_path=Path(
            str(
                files("lipidome_projector").joinpath(
                    "configuration/default_lipidome_data_config.toml"
                )
            )
        ),
        lipidome_anchor=files("lipidome_projector"),
        debug=False,
    )


if __name__ == "__main__":
    main()
