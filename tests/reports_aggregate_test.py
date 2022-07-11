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
        try:
            assert isinstance(reportsaggregate, dict)
        except KeyError:
            pytest.fail("expected a dict")

        try:
            assert isinstance(reportsaggregate["all_customer_stats"], dict)
        except KeyError:
            pytest.fail("expected a dict")

        try:
            assert isinstance(reportsaggregate["yearly_reports_sent"], int)
        except KeyError:
            pytest.fail("expected an int")
