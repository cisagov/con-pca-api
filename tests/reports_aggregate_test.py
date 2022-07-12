"""Test cases for reports aggregate related features."""

# Third-Party Libraries
import pytest


class TestSectorIndustries:
    """Test case for reports aggregate related views."""

    def test_sector_industrys_view(self, client):
        """Test the reports aggregates view."""
        resp = client.get("/api/reports/aggregate/")
        assert resp.status_code == 200

        self.check_sector_industry_properties(resp.json)

    @staticmethod
    def check_sector_industry_properties(reportsaggregate):
        """Check reportsaggregate object for expected properties."""
        if not isinstance(reportsaggregate, dict):
            pytest.fail("expected a dict")

        try:
            if not isinstance(reportsaggregate["all_customer_stats"], dict):
                pytest.fail("expected a dict")
        except KeyError:
            pytest.fail("all_customer_stats property does not exist")

        try:
            if not isinstance(reportsaggregate["yearly_reports_sent"], int):
                pytest.fail("expected an integer")
        except KeyError:
            pytest.fail("yearly_reports_sent property does not exist")
