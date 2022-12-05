"""Test cases for Overview -> Subscriptions Status."""

# Third-Party Libraries
import pytest


class TestSubscriptionStatus:
    """Test case for subscriptions status."""

    # def test_subscription_status_view(self, client):
    #     """Test the subscriptions status view."""
    #     resp = client.get("/api/subscriptions/status/")
    #     assert resp.status_code == 200

    #     self.check_subscription_status_properties(resp.json)

    @staticmethod
    def check_subscription_status_properties(subscription_status):
        """Check subscriptions status object for expected properties."""
        if not isinstance(subscription_status, list):
            pytest.fail("expected a list")

        if subscription_status:
            if not isinstance(subscription_status[0], dict):
                pytest.fail("expected a dict")

        if subscription_status[0]:
            assert subscription_status[0]["_id"] is not None
            if not isinstance(subscription_status[0]["primary_contact"], dict):
                pytest.fail("expected a dict")

            try:
                if not isinstance(
                    subscription_status[0]["primary_contact"]["email"], str
                ):
                    pytest.fail("expected a str")
            except KeyError:
                pytest.fail("email property does not exist")
