"""Application Config Views."""
# Third-Party Libraries
from flask import request
from flask.json import jsonify
from flask.views import MethodView

# cisagov Libraries
from api.config.application import AppConfig


class ConfigView(MethodView):
    """ConfigView."""

    def get(self):
        """Get config from database."""
        config = AppConfig()
        return jsonify(config.config)

    def put(self):
        """Modify the config."""
        config = AppConfig()
        return jsonify(config.update(request.json))
