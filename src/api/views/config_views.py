"""Application Config Views."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from flask import request
from flask.json import jsonify
from flask.views import MethodView
from marshmallow.exceptions import ValidationError

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
        try:
            return jsonify(config.update(request.json))
        except ValidationError as e:
            logging.exception(e)
            return jsonify(str(e)), 400
