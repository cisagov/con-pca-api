"""Test cases for recommendation related features."""

# Third-Party Libraries
import pytest

class Testrecommendations:
    """Test case for recommendation related views."""

    def test_recommendations_view(self, client):
        """Test the recommendations view."""
        resp = client.get("/api/recommendations/")
        assert resp.status_code == 200

        self.check_recommendation_properties(resp.json[0])

    def test_get_recommendation(self, client, recommendation):
        """Test the recommendation view."""
        recommendation_id = recommendation.get("_id")
        assert recommendation_id is not None

        resp = client.get(f"/api/recommendation/{recommendation_id}")
        assert resp.status_code == 200

        self.check_recommendation_properties(resp.json)

    @staticmethod
    def check_recommendation_properties(recommendation):
        """Check recommendation object for expected properties."""
        try:
            assert isinstance(recommendation["title"], str)
        except KeyError:
            pytest.fail("title property does not exist")

        try:
            assert recommendation["created_by"] == "bot"
        except KeyError:
            pytest.fail("created_by property does not exist")
            
        try:
            assert isinstance(recommendation["type"], str)
        except KeyError:
            pytest.fail("type property does not exist")

        try:
            assert isinstance(recommendation["description"], str)
        except KeyError:
            pytest.fail("description property does not exist")


