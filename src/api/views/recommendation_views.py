"""Recommendation Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from utils.recommendations import get_recommendations, save_recommendations


class RecommendationsView(MethodView):
    """RecommendationsView."""

    def get(self):
        """Get."""
        return jsonify(get_recommendations())

    def post(self):
        """Post."""
        save_recommendations(request.json)
        return jsonify({"success": True})
