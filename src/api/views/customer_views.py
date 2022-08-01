"""Customer views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CustomerManager, SubscriptionManager
from utils.sectors import SECTORS

customer_manager = CustomerManager()
subscription_manager = SubscriptionManager()


class CustomersView(MethodView):
    """CustomersView."""

    def get(self):
        """Get."""
        parameters = customer_manager.get_query(request.args)
        parameters["archived"] = {"$in": [False, None]}
        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        return jsonify(customer_manager.all(params=parameters))

    def post(self):
        """Post."""
        data = request.json
        return jsonify(customer_manager.save(data))


class CustomerView(MethodView):
    """CustomerView."""

    def get(self, customer_id):
        """Get."""
        return jsonify(customer_manager.get(document_id=customer_id))

    def put(self, customer_id):
        """Put."""
        customer_manager.update(document_id=customer_id, data=request.json)
        return jsonify({"success": True})

    def delete(self, customer_id):
        """Delete."""
        subscriptions = subscription_manager.all(
            params={"customer_id": customer_id},
            fields=["_id", "name"],
        )
        if subscriptions:
            return (
                jsonify(
                    {
                        "error": "Customer has active subscriptions.",
                        "subscriptions": subscriptions,
                    }
                ),
                400,
            )
        customer_manager.delete(document_id=customer_id)
        return jsonify({"success": True})


class SectorIndustryView(MethodView):
    """SectorIndustryView."""

    def get(self):
        """Get."""
        return jsonify(SECTORS)
