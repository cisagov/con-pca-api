"""Customer views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView
from utils.sectors import SECTORS

# cisagov Libraries
from api.manager import CustomerManager

customer_manager = CustomerManager()


class CustomersView(MethodView):
    """CustomersView."""

    def get(self):
        """Get."""
        return jsonify(
            customer_manager.all(params=customer_manager.get_query(request.args))
        )

    def post(self):
        """Post."""
        data = request.json
        # If a customer exists with either name or identifier, return 400
        if customer_manager.exists(
            {"identifier": data["identifier"]}
        ) or customer_manager.exists({"name": data["name"]}):
            return jsonify("Customer with identifier or name already exists."), 400
        return jsonify(customer_manager.save(data))


class CustomerView(MethodView):
    """CustomerView."""

    def get(self, customer_uuid):
        """Get."""
        customer = customer_manager.get(uuid=customer_uuid)
        return jsonify(customer)

    def put(self, customer_uuid):
        """Put."""
        return jsonify(customer_manager.update(uuid=customer_uuid, data=request.json))

    def delete(self, customer_uuid):
        """Delete."""
        return jsonify(customer_manager.delete(uuid=customer_uuid))


class SectorIndustryView(MethodView):
    """SectorIndustryView."""

    def get(self):
        """Get."""
        return jsonify(SECTORS)
