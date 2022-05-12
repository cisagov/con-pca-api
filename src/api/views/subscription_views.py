"""Subscription Views."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
from flask import jsonify, request, send_file
from flask.views import MethodView

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    SubscriptionManager,
    TargetManager,
)
from utils.notifications import Notification
from utils.safelist import generate_safelist_file
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

        subscriptions = subscription_manager.all(
            params=parameters,
            fields=[
                "_id",
                "customer_id",
                "name",
                "status",
                "start_date",
                "cycle_length_minutes",
                "active",
                "archived",
                "primary_contact",
                "admin_email",
                "target_email_list",
                "continuous_subscription",
                "created",
                "created_by",
                "updated",
                "updated_by",
            ],
        )
        if request.args.get("overview"):
            cycles = cycle_manager.all(fields=["subscription_id", "end_date"])
            subscriptions = [
                dict(s, **{"end_date": c["end_date"]})
                for c in cycles
                for s in subscriptions
                if c["subscription_id"] == s["_id"]
            ]

        return jsonify(subscriptions)

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
        if "target_email_list" in request.json:
            if not request.json["target_email_list"]:
                subscription = subscription_manager.get(
                    document_id=subscription_id, fields=["status"]
                )
                if subscription["status"] in ["queued", "running"]:
                    return (
                        jsonify(
                            {"error": "Subscription started, target list required."}
                        ),
                        400,
                    )
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
        resp, status_code = start_subscription(subscription_id)
        return jsonify(resp), status_code

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
        resp, status_code = test_subscription(subscription_id, request.json["contacts"])
        return jsonify(resp), status_code


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


class SubscriptionSafelistExportView(MethodView):
    """SubscriptionSafelistExportView."""

    def post(self, subscription_id):
        """
        Post.

        Get an excel file with safelist attributes in it.
        """
        data = request.json

        filepath = generate_safelist_file(
            subscription_id=subscription_id,
            phish_header=data["phish_header"],
            domains=data["domains"],
            ips=data["ips"],
            templates=data["templates"],
            reporting_password=data["password"],
            simulation_url=data.get("simulation_url", ""),
        )

        try:
            return send_file(
                filepath,
                as_attachment=True,
                attachment_filename="safelist_export.xlsx",
            )
        except Exception as e:
            logging.exception(e)
            raise e
        finally:
            logging.info(f"Deleting file {filepath}")
            os.remove(filepath)


class SubscriptionSafelistSendView(MethodView):
    """Send Safelisting Information Email."""

    def get(self, subscription_id):
        """Send Safelisting Information Email."""
        subscription = subscription_manager.get(document_id=subscription_id)
        cycle_filter_data = {
            "subscription_id": subscription["_id"],
        }
        if subscription["status"] not in ["created", "stopped"]:
            cycle_filter_data["active"] = True

        cycle = cycle_manager.get(filter_data=cycle_filter_data)

        filepath = ""
        Notification("safelisting_reminder", subscription, cycle).send()
        os.remove(filepath)

        return jsonify({"success": "Safelisting information email sent."})
