"""Recommendation Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import RecommendationManager, TemplateManager

recommendation_manager = RecommendationManager()
template_manager = TemplateManager()


class RecommendationsView(MethodView):
    """Recommendations View."""

    def get(self):
        """Get all recommendations."""
        return jsonify(recommendation_manager.all()), 200

    def post(self):
        """Create a new recommendation."""
        data = request.json
        if recommendation_manager.exists(
            {"title": data["title"], "description": data["description"]}
        ):
            return (
                jsonify({"error": "Recommendation with that name already exists."}),
                400,
            )
        recommendation_manager.save(data)
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
        # Check if recommendations are used on any templates
        templates_using = template_manager.all(
            params={
                "$or": [
                    {"sophisticated": recommendation_id},
                    {"red_flag": recommendation_id},
                ]
            }
        )
        if templates_using:
            return (
                jsonify(
                    {
                        "error": "Templates are currently utilizing this recommendation.",
                        "templates": templates_using,
                    }
                ),
                400,
            )
        recommendation_manager.delete(document_id=recommendation_id)
        return jsonify({"success": True}), 200
