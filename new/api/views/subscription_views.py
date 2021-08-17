"""Subscription Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView
from utils.subscriptions import (
    create_subscription_name,
    start_subscription,
    stop_subscription,
)

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager

subscription_manager = SubscriptionManager()
customer_manager = CustomerManager()
cycle_manager = CycleManager()


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
        print(request.json)
        resp = subscription_manager.update(uuid=subscription_uuid, data=request.json)
        print(resp)
        return jsonify(resp)

    def delete(self, subscription_uuid):
        """Delete."""
        subscription_manager.delete(uuid=subscription_uuid)
        cycle_manager.delete(params={"subscription_uuid": subscription_uuid})
        return jsonify({"success": True})


class SubscriptionLaunchView(MethodView):
    """SubscriptionLaunchView."""

    def get(self, subscription_uuid):
        """Launch a subscription."""
        return jsonify(start_subscription(subscription_uuid))

    def delete(self, subscription_uuid):
        """Stop a subscription."""
        return jsonify(stop_subscription(subscription_uuid))


class SubscriptionValidView(MethodView):
    """SubscriptionValidView."""

    def post(self):
        """Post."""
        return
