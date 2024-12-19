import sys
from flask import Flask
from service import config

api = None  # pylint: disable=invalid-name


############################################################
# Initialize the Flask instance
############################################################
def create_app():
    """Initialize the core application."""
    # Create Flask application
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Plugins
    # pylint: disable=import-outside-toplevel
    from service.models import db

    db.init_app(app)

    with app.app_context():
        # Dependencies require we import the routes AFTER the Flask app is created
        # pylint: disable=wrong-import-position, wrong-import-order, unused-import
        from service import (
            routes,
            models,
        )  # noqa: F401 E402 # pylint: disable=cyclic-import
        from service.common import cli_commands  # noqa: F401, E402

        try:
            db.create_all()
        except Exception as error:  # pylint: disable=broad-except
            app.logger.critical("%s: Cannot continue", error)
            sys.exit(4)

        return app
