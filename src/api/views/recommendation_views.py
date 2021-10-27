"""Recommendation Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import RecommendationManager

recommendation_manager = RecommendationManager()


class RecommendationsView(MethodView):
    """Recommendations View."""

    def get(self):
        """Get all recommendations."""
        return jsonify(recommendation_manager.all()), 200

    def post(self):
        """Create a new recommendation."""
        recommendation_manager.save(request.json)
        return jsonify({"success": True}), 200


class RecommendationView(MethodView):
    """Recommendation Detail View."""

    def get(self, recommendation_id):
        """Get recommendation details."""
        return jsonify(recommendation_manager.get(document_id=recommendation_id)), 200

    def put(self, recommendation_id):
        """Update recommendation details."""
        recommendation_manager.update(document_id=recommendation_id, data=request.json)
        return jsonify({"success": True}), 200

    def delete(self, recommendation_id):
        """Delete a recommendation."""
        recommendation_manager.delete(document_id=recommendation_id)
        return jsonify({"success": True}), 200
