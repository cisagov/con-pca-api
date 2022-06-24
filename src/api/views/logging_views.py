"""Logging views."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from api.manager import LoggingManager

logging_manager = LoggingManager()


class LoggingView(MethodView):
    """LoggingView."""

    def get(self):
        """Get."""
        logging.error("this is a test.")
        return jsonify(logging_manager.all())
