"""Test cases for subscription related features."""

# Third-Party Libraries
import pytest


class TestSubscriptions:
    """Test case for subscription related views."""

    # Commenting this test out because Mongomock does not support the type conversion operators we need to use
    # def test_subscriptions_view(self, client):
    #     """Test the subscriptions view."""
    #     resp = client.get("/api/subscriptions/")
    #     assert resp.status_code == 200

    #     self.check_subscription_properties(resp.json[0])

    def test_get_subscription(self, client, subscription):
        """Test the subscription view."""
        sub_id = subscription.get("_id")
        assert sub_id is not None

        resp = client.get(f"/api/subscription/{sub_id}/")
        assert resp.status_code == 200

        self.check_subscription_properties(resp.json)

    @staticmethod
    def check_subscription_properties(sub):
        """Check subscription object for expected properties."""
        try:
            if not isinstance(sub["name"], str):
                pytest.fail("expected a string")
        except KeyError:
            pytest.fail("name property does not exist")

        try:
            if not isinstance(sub["created_by"], str):
                pytest.fail("expected a string")
        except KeyError:
            pytest.fail("created_by property does not exist")

        try:
            if not isinstance(sub["continuous_subscription"], bool):
                pytest.fail("expected a boolean")
        except KeyError:
            pytest.fail("continuous_subscription property does not exist")

        try:
            if not isinstance(sub["target_email_list"], list):
                pytest.fail("expected a list")
        except KeyError:
            pytest.fail("target_email_list property does not exist")

        try:
            if not isinstance(sub["templates_selected"], list):
                pytest.fail("expected a list")
        except KeyError:
            pytest.fail("templates_selected property does not exist")

        try:
            if not isinstance(sub["processing"], bool):
                pytest.fail("expected a boolean")
        except KeyError:
            pytest.fail("processing property does not exist")

        if sub.get("tasks", None):
            if not isinstance(sub["tasks"][0]["executed"], bool):
                pytest.fail("expected a boolean")
