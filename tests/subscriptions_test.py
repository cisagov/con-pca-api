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

        def _check(key):
            try:
                return sub[key]
            except KeyError:
                raise ValueError(f"{key} does not exist in subscription object")

        with pytest.raises(ValueError):
            assert _check("does_not_exist") == "nope"

        assert (
            _check("name") == "test_subscription"
        ), "name does not match expected value"

        assert _check("created_by") == "bot", "created_by does not match expected value"

        assert (
            _check("continuous_subscription") is False
        ), "continuous_subscription does not match expected value"

        target_email_list = _check("target_email_list")
        assert isinstance(target_email_list, list), "target_email_list is not a list"
        assert (
            len(target_email_list) == 4
        ), "length of target_email_list does not match expected value"
