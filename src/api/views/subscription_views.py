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
from utils.safelist_testing import test_subscription
from utils.subscriptions import (
    create_subscription_name,
    get_random_phish_header,
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
        parameters = subscription_manager.get_query(parameters)

        if request.args.get("template"):
            cycles = cycle_manager.all(
                params={"template_ids": request.args["template"]},
                fields=["subscription_id"],
            )
            subscription_ids = list({c["subscription_id"] for c in cycles})
            parameters["$or"] = [
                {"_id": {"$in": subscription_ids}},
                {"templates_selected": request.args["template"]},
            ]

        parameters["archived"] = {"$in": [False, None]}
        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        return jsonify(
            subscription_manager.all(
                params=parameters,
                fields=[
                    "_id",
                    "customer_id",
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
        customer = customer_manager.get(document_id=subscription["customer_id"])
        subscription["name"] = create_subscription_name(customer)
        subscription["status"] = "created"
        subscription["phish_header"] = get_random_phish_header()
        response = subscription_manager.save(subscription)
        response["name"] = subscription["name"]
        return jsonify(response)


class SubscriptionView(MethodView):
    """SubscriptionView."""

    def get(self, subscription_id):
        """Get."""
        return jsonify(subscription_manager.get(document_id=subscription_id))

    def put(self, subscription_id):
        """Put."""
        subscription_manager.update(document_id=subscription_id, data=request.json)
        return jsonify({"success": True})

    def delete(self, subscription_id):
        """Delete."""
        subscription_manager.delete(document_id=subscription_id)
        cycle_manager.delete(params={"subscription_id": subscription_id})
        target_manager.delete(params={"subscription_id": subscription_id})
        return jsonify({"success": True})


class SubscriptionLaunchView(MethodView):
    """SubscriptionLaunchView."""

    def get(self, subscription_id):
        """Launch a subscription."""
        return jsonify(start_subscription(subscription_id))

    def delete(self, subscription_id):
        """Stop a subscription."""
        return jsonify(stop_subscription(subscription_id))


class SubscriptionTestView(MethodView):
    """SubscriptionTestView."""

    def get(self, subscription_id):
        """Get test results for a subscription."""
        return jsonify(
            subscription_manager.get(
                document_id=subscription_id, fields=["test_results"]
            ).get("test_results", [])
        )

    def post(self, subscription_id):
        """Launch a test for the subscription."""
        return jsonify(test_subscription(subscription_id))


class SubscriptionValidView(MethodView):
    """SubscriptionValidView."""

    def post(self):
        """Post."""
        data = request.json
        return jsonify(
            is_subscription_valid(
                data["target_count"],
                data["cycle_minutes"],
            )
        )


class SubscriptionHeaderView(MethodView):
    """SubscriptionHeaderView."""

    def get(self, subscription_id):
        """
        Get.

        Rotate the subscription phishing header.
        """
        new_header = get_random_phish_header()
        subscription_manager.update(
            document_id=subscription_id, data={"phish_header": new_header}
        )
        return jsonify({"phish_header": new_header})
