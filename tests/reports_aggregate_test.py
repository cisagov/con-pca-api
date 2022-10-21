"""Test cases for reports aggregate related features."""

# Third-Party Libraries
import pytest


class TestReportsAggregate:
    """Test case for reports aggregate related views."""

    def test_reports_aggregate_view(self, client):
        """Test the reports aggregates view."""
        resp = client.get("/api/reports/aggregate/")
        assert resp.status_code == 200

        self.check_reports_aggregate_properties(resp.json)

    @staticmethod
    def check_reports_aggregate_properties(reportsaggregate):
        """Check reportsaggregate object for expected properties."""
        if not isinstance(reportsaggregate, dict):
            pytest.fail("expected a dict")

        try:
            if not isinstance(reportsaggregate["all_customer_stats"], dict):
                pytest.fail("expected a dict")
        except KeyError:
            pytest.fail("all_customer_stats property does not exist")
