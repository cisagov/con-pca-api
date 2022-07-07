"""Test cases for cycle related features."""

# Third-Party Libraries
import pytest


class TestCycles:
    """Test case for cycle related views."""

    def test_cycles_view(self, client):
        """Test the cycles view."""
        resp = client.get("/api/cycles/")
        assert resp.status_code == 200

        self.check_cycle_properties(resp.json[0])

    def test_get_cycle(self, client, cycle):
        """Test the cycle view."""
        cycle_id = cycle.get("_id")
        assert cycle_id is not None

        resp = client.get(f"/api/cycle/{cycle_id}")
        assert resp.status_code == 200

        self.check_cycle_properties(resp.json)

    @staticmethod
    def check_cycle_properties(cycle):
        """Check cycle object for expected properties."""
        try:
            assert isinstance(cycle["subscription_id"], str)
        except KeyError:
            pytest.fail("subscription_id property does not exist")

        try:
            assert isinstance(cycle["target_count"], int)
        except KeyError:
            pytest.fail("target_count property does not exist")

        try:
            assert isinstance(cycle["active"], bool)
        except KeyError:
            pytest.fail("active property does not exist")

        try:
            assert isinstance(cycle["template_ids"], list)
            assert len(cycle["template_ids"]) <= 3
        except KeyError:
            pytest.fail("template_ids property does not exist")
