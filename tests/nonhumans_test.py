"""Test cases for nonhuman related features."""

# Third-Party Libraries
import pytest

class TestNonhumans:
    """Test case for nonhuman related views."""

    def test_nonhumans_view(self, client):
        """Test the nonhumans view."""
        resp = client.get("/api/nonhumans/")
        assert resp.status_code == 200

        self.check_nonhuman_properties(resp.json)

    @staticmethod
    def check_nonhuman_properties(nonhuman):
        """Check nonhuman object for expected properties."""
        try:
            assert isinstance(nonhuman[0], str)
        except KeyError:
            pytest.fail("expected a string")
            
        try:
            assert isinstance(nonhuman, list)
            assert len(nonhuman) >= 3
        except KeyError:
            pytest.fail("expected a list of at least length 3")
            

