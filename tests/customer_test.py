"""Test cases for customer related features."""

# Third-Party Libraries
import pytest


class TestCustomers:
    """Test case for customer related views."""

    def test_customers_view(self, client):
        """Test the customers view."""
        resp = client.get("/api/customers/")
        assert resp.status_code == 200

        self.check_customer_properties(resp.json[0])

    def test_get_customer(self, client, customer):
        """Test the customer view."""
        customer_id = customer.get("_id")
        assert customer_id is not None

        resp = client.get(f"/api/customer/{customer_id}")
        assert resp.status_code == 200

        self.check_customer_properties(resp.json)

    @staticmethod
    def check_customer_properties(customer):
        """Check customer object for expected properties."""
        try:
            assert isinstance(customer["customer_type"], str)
        except KeyError:
            pytest.fail("customer_type property does not exist")

        try:
            assert isinstance(customer["name"], str)
        except KeyError:
            pytest.fail("name property does not exist")

        try:
            assert isinstance(customer["contact_list"], list)
            assert len(customer["contact_list"]) <= 1
        except KeyError:
            pytest.fail("contact_list property does not exist")

        try:
            assert isinstance(customer["contact_list"][0]["email"], str)
        except KeyError:
            pytest.fail("email property does not exist")
