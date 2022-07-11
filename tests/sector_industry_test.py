"""Test cases for sector industry related features."""

# Third-Party Libraries
import pytest


class TestSectorIndustries:
    """Test case for sector industry related views."""

    def test_sector_industrys_view(self, client):
        """Test the sector industrys view."""
        resp = client.get("/api/sectorindustry/")
        assert resp.status_code == 200

        self.check_sector_industry_properties(resp.json)


    @staticmethod
    def check_sector_industry_properties(sectorindustry):
        """Check sectorindustry object for expected properties."""
        try:
            assert isinstance(sectorindustry, list)
        except KeyError:
            pytest.fail("expected a list")

        try:
            assert isinstance(sectorindustry[0], dict)
        except KeyError:
            pytest.fail("sectorindustry list is empty")

        try:
            assert isinstance(sectorindustry[0]["industries"], list)
        except KeyError:
            pytest.fail("industries property does not exist")

        try:
            assert isinstance(sectorindustry[0]["industries"][0]["name"], str)
        except KeyError:
            pytest.fail("name property does not exist")
