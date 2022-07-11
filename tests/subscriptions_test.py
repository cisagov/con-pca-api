"""Test cases for subscription related features."""

# Third-Party Libraries
import pytest


class TestSubscriptions:
    """Test case for subscription related views."""

    def test_subscriptions_view(self, client):
        """Test the subscriptions view."""
        resp = client.get("/api/subscriptions/")
        assert resp.status_code == 200

        self.check_subscription_properties(resp.json[0])

    def test_get_subscription(self, client, subscription):
        """Test the subscription view."""
        sub_id = subscription.get("_id")
        assert sub_id is not None

        resp = client.get(f"/api/subscription/{sub_id}")
        assert resp.status_code == 200

        self.check_subscription_properties(resp.json)

    @staticmethod
    def check_subscription_properties(sub):
        """Check subscription object for expected properties."""
        try:
            assert isinstance(sub["name"], str)
        except KeyError:
            pytest.fail("name property does not exist")

        try:
            assert isinstance(sub["created_by"], str)
        except KeyError:
            pytest.fail("created_by property does not exist")

        try:
            assert isinstance(sub["continuous_subscription"], bool)
        except KeyError:
            pytest.fail("continuous_subscription property does not exist")

        try:
            target_email_list = sub["target_email_list"]
            assert isinstance(target_email_list, list)
        except KeyError:
            pytest.fail("target_email_list property does not exist")
