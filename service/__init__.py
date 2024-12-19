import sys
from flask import Flask
from flask_restx import Api
from service import config
from service.common import log_handlers

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

    ######################################################################
    # Configure Swagger before initializing it
    ######################################################################
    global api
    api = Api(
        app,
        version="1.0.0",
        title="Reservations REST API Service",
        description="This is a Reservations server.",
        default="reservations",
        default_label="Reservations operations",
        doc="/apidocs",  # default also could use doc='/apidocs/'
        prefix="/api",
    )

    with app.app_context():
        # Dependencies require we import the routes AFTER the Flask app is created
        # pylint: disable=wrong-import-position, wrong-import-order, unused-import
        from service import (
            routes,
            models,
        )  # noqa: F401 E402 # pylint: disable=cyclic-import
        from service.common import error_handlers, cli_commands  # noqa: F401, E402

        try:
            db.create_all()
        except Exception as error:  # pylint: disable=broad-except
            app.logger.critical("%s: Cannot continue", error)
            sys.exit(4)

        # Set up logging for production
        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
        app.logger.info(70 * "*")

        app.logger.info("Service initialized!")

        return app
