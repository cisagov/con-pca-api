"""Subscription Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    SubscriptionManager,
    TargetManager,
)
from utils.subscriptions import (
    create_subscription_name,
    start_subscription,
    stop_subscription,
)
from utils.valid import is_subscription_valid

subscription_manager = SubscriptionManager()
customer_manager = CustomerManager()
cycle_manager = CycleManager()
target_manager = TargetManager()


class SubscriptionsView(MethodView):
    """SubscriptionsView."""

    def get(self):
        """Get."""
        parameters = dict(request.args)

        # TODO: Allow querying by template
        parameters = subscription_manager.get_query(parameters)

        if request.args.get("template"):
            cycles = cycle_manager.all(
                params={"template_uuids": request.args["template"]},
                fields=["subscription_uuid"],
            )
            subscription_uuids = list({c["subscription_uuid"] for c in cycles})
            parameters["$or"] = [
                {"subscription_uuid": {"$in": subscription_uuids}},
                {"templates_selected.low": request.args["template"]},
                {"templates_selected.moderate": request.args["template"]},
                {"templates_selected.high": request.args["template"]},
            ]

        parameters["archived"] = {"$in": [False, None]}
        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

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
        subscription_manager.update(uuid=subscription_uuid, data=request.json)
        return jsonify({"success": True})

    def delete(self, subscription_uuid):
        """Delete."""
        subscription_manager.delete(uuid=subscription_uuid)
        cycle_manager.delete(params={"subscription_uuid": subscription_uuid})
        target_manager.delete(params={"subscription_uuid": subscription_uuid})
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
        data = request.json
        is_valid, message = is_subscription_valid(
            data["target_count"],
            data["cycle_minutes"],
        )
        if is_valid:
            return jsonify({"success": "Subscription is valid."}), 200
        else:
            return jsonify({"error": message}), 400
