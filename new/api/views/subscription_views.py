"""Subscription Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView
from utils.subscriptions import create_subscription_name

# cisagov Libraries
from api.manager import CustomerManager, SubscriptionManager

subscription_manager = SubscriptionManager()
customer_manager = CustomerManager()


class SubscriptionsView(MethodView):
    """SubscriptionsView."""

    def get(self):
        """Get."""
        parameters = dict(request.args)

        parameters["archived"] = {"$in": [False, None]}
        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True
        # TODO: Allow querying by template
        parameters = subscription_manager.get_query(parameters)

        return jsonify(
            subscription_manager.all(
                params=parameters,
                fields=[
                    "subscription_uuid",
                    "customer_uuid",
                    "name",
                    "status",
                    "start_date",
                    "active",
                    "archived",
                    "primary_contact",
                    "admin_email",
                ],
            )
        )

    def post(self):
        """Post."""
        subscription = request.json
        customer = customer_manager.get(uuid=subscription["customer_uuid"])
        subscription["name"] = create_subscription_name(customer)
        subscription["status"] = "created"
        response = subscription_manager.save(subscription)
        response["name"] = subscription["name"]
        return jsonify(response)


class SubscriptionView(MethodView):
    """SubscriptionView."""

    def get(self, subscription_uuid):
        """Get."""
        return jsonify(subscription_manager.get(uuid=subscription_uuid))

    def put(self, subscription_uuid):
        """Put."""
        return jsonify(
            subscription_manager.update(uuid=subscription_uuid, data=request.json)
        )

    def delete(self, subscription_uuid):
        """Delete."""
        return jsonify(subscription_manager.delete(uuid=subscription_uuid))
