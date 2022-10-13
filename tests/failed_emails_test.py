"""Test cases for failed emails"""

# Third-Party Libraries
import pytest


class TestFailedEmails:
    """Test case for failed emails."""

    def test_failed_emails_view(self, client):
        """Test the failed emails view."""
        resp = client.get("/api/failedemails/")
        assert resp.status_code == 200

        self.check_failed_emails_properties(resp.json)

    @staticmethod
    def check_failed_emails_properties(failed_emails):
        """Check failed_emails object for expected properties."""
        if not isinstance(failed_emails, dict):
            pytest.fail("expected a dict")

        if failed_emails:
            if not isinstance(failed_emails["failed_emails"], list):
                pytest.fail("expected a list")

        if failed_emails["failed_emails"]:
            if not isinstance(failed_emails["failed_emails"][0], dict):
                pytest.fail("expected a dict")

            try:
                if not isinstance(failed_emails["failed_emails"][0]["reason"], str):
                    pytest.fail("expected a str")
            except KeyError:
                pytest.fail("reason property does not exist")
