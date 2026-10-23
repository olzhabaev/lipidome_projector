"""Lipidome projector entry point."""

import logging

from dash import Dash
from flask import Flask

from lipidome_projector.app_creation import create_default_app

logger: logging.Logger = logging.getLogger(__name__)


app: Dash = create_default_app()


server: Flask = app.server


def main() -> None:
    logger.info("Run server.")
    app.run(debug=False, host="0.0.0.0", port=8050, use_reloader=False)


if __name__ == "__main__":
    main()
