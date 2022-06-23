"""Logging views."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from api.config.environment import DB
from api.manager import LoggingManager

logging_manager = LoggingManager()
logging_collection = getattr(DB, "logging")


class LoggingView(MethodView):
    """LoggingView."""

    def get(self):
        """Get."""
        return jsonify(logging_manager.all())

    def post(self):
        """Post."""
        logging.error("We just raised an error on purpose! Is the logger working?")
        return jsonify(logging_manager.all())

    def delete(self):
        """Delete."""
        logging_manager.delete(params={"created_by": "bot"})
        return jsonify(logging_manager.all())


class LoggingTTLView(MethodView):
    """LoggingTTLView."""

    def get(self):
        """Get."""
        return jsonify(
            logging_collection.index_information()["datetime_1"]["expireAfterSeconds"]
        )  # Return the current ttl parameter

    def post(self, ttl_in_seconds):
        """Post."""
        if "datetime_1" not in logging_collection.index_information():
            logging_collection.create_index(
                "datetime", expireAfterSeconds=ttl_in_seconds
            )
            return jsonify(
                logging_collection.index_information()["datetime_1"][
                    "expireAfterSeconds"
                ]
            )
        else:
            logging.error(
                "Operation failed, TTL has been set previously with value {ttl}".format(
                    ttl=logging_collection.index_information()["datetime_1"][
                        "expireAfterSeconds"
                    ]
                )
            )
            return jsonify(logging_manager.all())

    def put(self, ttl_in_seconds):
        """Put."""
        ttl_in_seconds = int(ttl_in_seconds)
        DB.command(
            "collMod",
            "logging",
            index={"name": "datetime_1", "expireAfterSeconds": ttl_in_seconds},
        )  # Change the TTL if it has already been set
        return jsonify(
            logging_collection.index_information()["datetime_1"]["expireAfterSeconds"]
        )
