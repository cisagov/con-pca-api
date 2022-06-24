"""Logging views."""
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
        return jsonify(logging_manager.all())
