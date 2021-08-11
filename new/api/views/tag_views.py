"""Tag views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView
from utils.tags import TAGS


class TagsView(MethodView):
    """TagsView."""

    def get(self):
        """Get."""
        return jsonify(TAGS)
