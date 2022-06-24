"""Test cases for subscription related features."""

# Standard Python Libraries
import logging

# Third-Party Libraries
import pytest

log = logging.getLogger(__name__)


class TestSubscriptions:
    """Test case for subscription related views."""

    def test_subscriptions_view(self, client):
        """Test the subscriptions view."""
        resp = client.get("/api/subscriptions/")
        assert resp.status_code == 200

        sub = resp.json[0]
        self.check_subscription_properties(sub)

    def test_get_subscription(self, client, subscription):
        """Test the subscription view."""
        sub_id = subscription.get("_id")
        assert sub_id is not None

        resp = client.get(f"/api/subscription/{sub_id}")
        assert resp.status_code == 200

        sub = resp.json
        self.check_subscription_properties(sub)

    @staticmethod
    def check_subscription_properties(sub):
        """Check subscription object for expected properties."""
        try:
            assert sub["name"] == "test_subscription"
        except KeyError:
            pytest.fail("name property does not exist")

        try:
            assert sub["created_by"] == "bot"
        except KeyError:
            pytest.fail("created_by property does not exist")

        try:
            assert sub["continuous_subscription"] is False
        except KeyError:
            pytest.fail("continuous_subscription property does not exist")

        try:
            target_email_list = sub["target_email_list"]
            assert isinstance(target_email_list, list)
            assert len(target_email_list) == 4
        except KeyError:
            pytest.fail("target_email_list property does not exist")
