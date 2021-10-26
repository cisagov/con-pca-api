"""Recommendation Utils."""
# Standard Python Libraries
import json

# cisagov Libraries
from api.manager import RecommendationManager

recommendation_manager = RecommendationManager()


def get_recommendations():
    """Get recommendations from db."""
    with open("static/recommendations.json", "r") as f:
        response = json.load(f)
    recommendations = recommendation_manager.all()
    for recommendation in recommendations:
        value = recommendation["value"]
        if recommendation["type"] == "level":
            response["levels"][recommendation["value"]][
                "recommendation"
            ] = recommendation["recommendation"]
        elif recommendation["type"] == "indicator":
            group = recommendation["group"]
            indicator = recommendation["indicator"]

            if (
                group in response["indicators"]
                and indicator in response["indicators"][group]
            ):
                response["indicators"][group][indicator]["values"][value][
                    "recommendation"
                ] = recommendation["recommendation"]

    return response
