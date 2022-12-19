"""Subscription Views."""
# Standard Python Libraries
from collections import OrderedDict
from datetime import timedelta
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
    TemplateManager,
)
from utils.logging import setLogger
from utils.notifications import Notification
from utils.safelist import generate_safelist_file
from utils.safelist_testing import test_subscription
from utils.subscriptions import (
    create_subscription_name,
    get_random_phish_header,
    start_subscription,
    stop_subscription,
)
from utils.templates import select_templates
from utils.valid import is_subscription_valid

logger = setLogger(__name__)

subscription_manager = SubscriptionManager()
customer_manager = CustomerManager()
cycle_manager = CycleManager()
target_manager = TargetManager()
template_manager = TemplateManager()


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
            subscriptions = subscription_manager.all(
                params=parameters,
                fields=[
                    "_id",
                    "name",
                    "status",
                ],
            )
            return subscriptions

        parameters["archived"] = False
        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        # pipeline = [
        #     {
        #         "$match": {"archived": {"$in": [False, None]}}
        #         if not parameters["archived"]
        #         else {"archived": {"$nin": [False, None]}}
        #     },
        #     {
        #         "$addFields": {
        #             "subscription_id": {"$toString": "$_id"},
        #             "customer_object_id": {"$toObjectId": "$customer_id"},
        #         }
        #     },
        #     {
        #         "$lookup": {
        #             "from": "cycle",
        #             "localField": "subscription_id",
        #             "foreignField": "subscription_id",
        #             "as": "cycle",
        #         }
        #     },
        #     {
        #         "$lookup": {
        #             "from": "customer",
        #             "localField": "customer_object_id",
        #             "foreignField": "_id",
        #             "as": "customer",
        #         }
        #     },
        #     {
        #         "$project": {
        #             "_id": {"$toString": "$_id"},
        #             "appendix_a_date": {"$max": "$customer.appendix_a_date"},
        #             "cycle_start_date": {"$max": "$cycle.start_date"},
        #             "created": "$created",
        #             "target_domain": "$target_domain",
        #             "customer_id": "$customer_id",
        #             "name": "$name",
        #             "status": "$status",
        #             "start_date": "$start_date",
        #             "cycle_length_minutes": "$cycle_length_minutes",
        #             "cooldown_minutes": "$cooldown_minutes",
        #             "buffer_time_minutes": "$buffer_time_minutes",
        #             "active": {"$anyElementTrue": "$cycle.active"},
        #             "archived": "$archived",
        #             "primary_contact": "$primary_contact",
        #             "admin_email": "$admin_email",
        #             "target_email_list": "$target_email_list",
        #             "continuous_subscription": "$continuous_subscription",
        #             "created_by": "$created_by",
        #             "updated": "$updated",
        #             "updated_by": "$updated_by",
        #         }
        #     },
        # ]

        # subscriptions = subscription_manager.aggregate(pipeline)

        subscriptions = subscription_manager.all(
            params=parameters,
            fields=[
                "_id",
                "customer_id",
                "name",
                "status",
                "start_date",
                "cycle_length_minutes",
                "cooldown_minutes",
                "buffer_time_minutes",
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
                "target_domain",
            ],
        )
        cycles = cycle_manager.all(
            fields=["subscription_id", "start_date", "end_date", "active"]
        )
        subscriptions = [
            dict(
                s,
                **{
                    "cycle_start_date": c.get("start_date", ""),
                    "cycle_end_date": c.get("end_date", ""),
                    "active": c.get("active", ""),
                },
            )
            for c in cycles
            for s in subscriptions
            if c.get("subscription_id") == s.get("_id")
        ]
        for s in subscriptions:
            c = customer_manager.get(
                document_id=s["customer_id"], fields=["_id", "appendix_a_date"]
            )
            s["appendix_a_date"] = c.get("appendix_a_date", "")
        subscriptions = sorted(subscriptions, key=lambda d: d["cycle_start_date"])
        subscriptions = list(
            OrderedDict((d["name"], d) for d in subscriptions).values()
        )

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
        return jsonify(
            subscription_manager.get(
                document_id=subscription_id,
            )
        )

    def put(self, subscription_id):
        """Put."""
        subscription = subscription_manager.get(
            document_id=subscription_id,
            fields=["status", "continuous_subscription"],
        )
        if subscription["status"] in ["queued", "running"]:
            if "continuous_subscription" in request.json:
                if request.json["continuous_subscription"] != subscription.get(
                    "continuous_subscription"
                ):
                    data = {}
                    data["tasks"] = subscription["tasks"]
                    if request.json["continuous_subscription"]:
                        for task in data["tasks"]:
                            if task["task_type"] == "end_cycle":
                                task["task_type"] = "start_next_cycle"
                                task["scheduled_date"] = task[
                                    "scheduled_date"
                                ] + timedelta(
                                    minutes=(subscription.get("buffer_time_minutes", 0))
                                )
                        subscription_manager.update(
                            document_id=subscription_id, data=data
                        )
                    else:
                        for task in data["tasks"]:
                            if task["task_type"] == "start_next_cycle":
                                task["task_type"] = "end_cycle"
                                task["scheduled_date"] = task[
                                    "scheduled_date"
                                ] - timedelta(
                                    minutes=(subscription.get("buffer_time_minutes", 0))
                                )
                        subscription_manager.update(
                            document_id=subscription_id, data=data
                        )

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


class SubscriptionsStatusView(MethodView):
    """SubscriptionStatusView."""

    def get(self):
        """Get data for the Overview Subscription Status Page."""
        # pipeline = [
        #     {"$match": {"archived": {"$in": [False, None]}}},
        #     {
        #         "$addFields": {
        #             "subscription_id": {"$toString": "$_id"},
        #             "customer_object_id": {"$toObjectId": "$customer_id"},
        #         }
        #     },
        #     {
        #         "$lookup": {
        #             "from": "cycle",
        #             "localField": "subscription_id",
        #             "foreignField": "subscription_id",
        #             "as": "cycle",
        #         }
        #     },
        #     {
        #         "$lookup": {
        #             "from": "customer",
        #             "localField": "customer_object_id",
        #             "foreignField": "_id",
        #             "as": "customer",
        #         }
        #     },
        #     {
        #         "$project": {
        #             "_id": {"$toString": "$_id"},
        #             "appendix_a_date": {"$max": "$customer.appendix_a_date"},
        #             "cycle_start_date": {"$max": "$cycle.start_date"},
        #             "cycle_end_date": {"$max": "$cycle.end_date"},
        #             "active": {"$anyElementTrue": "$cycle.active"},
        #             "created": "$created",
        #             "target_domain": "$target_domain",
        #             "customer_id": "$customer_id",
        #             "name": "$name",
        #             "status": "$status",
        #             "start_date": "$start_date",
        #             "cycle_length_minutes": "$cycle_length_minutes",
        #             "cooldown_minutes": "$cooldown_minutes",
        #             "buffer_time_minutes": "$buffer_time_minutes",
        #             "archived": "$archived",
        #             "primary_contact": "$primary_contact",
        #             "admin_email": "$admin_email",
        #             "target_email_list": "$target_email_list",
        #             "continuous_subscription": "$continuous_subscription",
        #             "created_by": "$created_by",
        #             "updated": "$updated",
        #             "updated_by": "$updated_by",
        #         }
        #     },
        # ]
        # # subscriptions = subscription_manager.aggregate(pipeline)

        # return subscriptions

        parameters = dict(request.args)
        parameters = subscription_manager.get_query(parameters)

        subscriptions = subscription_manager.all(
            params=parameters,
            fields=[
                "_id",
                "customer_id",
                "name",
                "status",
                "start_date",
                "cycle_length_minutes",
                "cooldown_minutes",
                "buffer_time_minutes",
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
                "target_domain",
            ],
        )
        # TODO: refactor to leverage mongo queries.
        cycles = cycle_manager.all(
            fields=["subscription_id", "start_date", "end_date", "active"]
        )
        subscriptions = [
            dict(
                s,
                **{
                    "cycle_start_date": c["start_date"],
                    "cycle_end_date": c["end_date"],
                    "active": c["active"],
                },
            )
            for c in cycles
            for s in subscriptions
            if c["subscription_id"] == s["_id"]
        ]
        for s in subscriptions:
            c = customer_manager.get(
                document_id=s["customer_id"], fields=["_id", "appendix_a_date"]
            )
            s["appendix_a_date"] = c.get("appendix_a_date", "")
        subscriptions = sorted(subscriptions, key=lambda d: d["cycle_start_date"])
        subscriptions = list(
            OrderedDict((d["name"], d) for d in subscriptions).values()
        )

        return jsonify(subscriptions)


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
        subscription = subscription_manager.get(document_id=subscription_id)

        data = request.json

        # Randomize Next templates if they do not already exist
        if not subscription.get("next_templates"):
            update_data = {}
            next_templates = [
                t
                for t in template_manager.all({"retired": False})
                if t not in subscription.get("templates_selected")
            ]
            next_templates_selected = sum(select_templates(next_templates), [])
            if next_templates_selected:
                update_data["next_templates"] = next_templates_selected
            subscription_manager.update(document_id=subscription_id, data=update_data)
        else:
            next_templates_selected = subscription.get("next_templates", [])

        data["next_templates"] = template_manager.all(
            params={"_id": {"$in": next_templates_selected}},
            fields=["subject", "deception_score"],
        )

        filepath = generate_safelist_file(
            subscription_id=subscription_id,
            phish_header=data["phish_header"],
            domains=data["domains"],
            ips=data["ips"],
            templates=data["templates"],
            next_templates=data["next_templates"],
            reporting_password=data["password"],
            simulation_url=data.get("simulation_url", ""),
        )

        try:
            return send_file(
                filepath,
                as_attachment=True,
                download_name="safelist_export.xlsx",
            )
        except Exception as e:
            logger.error(
                "Failed to generate safelisting file.",
                exc_info=e,
                extra={
                    "source_type": "subscription",
                    "source": subscription_id,
                },
            )
            raise e
        finally:
            logger.info(f"Deleting safelisting file {filepath}")
            os.remove(filepath)


class SubscriptionSafelistSendView(MethodView):
    """Send Safelisting Information Email."""

    def post(self, subscription_id):
        """Send Safelisting Information Email."""
        subscription = subscription_manager.get(document_id=subscription_id)
        cycle_filter_data = {
            "subscription_id": subscription["_id"],
        }
        if subscription["status"] not in ["created", "stopped"]:
            cycle_filter_data["active"] = True

        cycle = cycle_manager.get(filter_data=cycle_filter_data)

        data = request.json

        # Randomize Next templates if they do not already exist
        if not subscription.get("next_templates"):
            update_data = {}
            next_templates = [
                t
                for t in template_manager.all({"retired": False})
                if t not in subscription.get("templates_selected")
            ]
            next_templates_selected = sum(select_templates(next_templates), [])
            if next_templates_selected:
                update_data["next_templates"] = next_templates_selected
            subscription_manager.update(document_id=subscription_id, data=update_data)
        else:
            next_templates_selected = subscription.get("next_templates", [])

        data["next_templates"] = template_manager.all(
            params={"_id": {"$in": next_templates_selected}},
            fields=["subject", "deception_score"],
        )

        filepath = generate_safelist_file(
            subscription_id=subscription_id,
            phish_header=data["phish_header"],
            domains=data["domains"],
            ips=data["ips"],
            templates=data["templates"],
            next_templates=data["next_templates"],
            reporting_password=data["password"],
            simulation_url=data.get("simulation_url", ""),
        )

        if not os.path.exists(filepath):
            logger.error(
                "Safelist file does not exist: " + filepath,
                extra={
                    "source_type": "subscription",
                    "source": subscription_id,
                },
            )
            return (
                jsonify({"success": "Failed to generate safelisting file."}),
                500,
            )

        Notification("safelisting_reminder", subscription, cycle).send(
            attachments=[filepath]
        )

        return jsonify({"success": "Safelisting information email sent."})


class SubscriptionCurrentTemplatesView(MethodView):
    """Get the current templates for a given subscription."""

    def get(self, subscription_id):
        """Get test results for a subscription."""
        template_ids = subscription_manager.get(
            document_id=subscription_id, fields=["templates_selected"]
        ).get("templates_selected", [])
        templates = template_manager.all(
            params={"_id": {"$in": template_ids}},
            fields=["subject"],
        )
        return jsonify([t["subject"] for t in templates if "subject" in t])


class SubscriptionNextTemplatesView(MethodView):
    """Get the next templates for a given subscription."""

    def get(self, subscription_id):
        """Get test results for a subscription."""
        template_ids = subscription_manager.get(
            document_id=subscription_id, fields=["next_templates"]
        ).get("next_templates", [])
        templates = template_manager.all(
            params={"_id": {"$in": template_ids}},
            fields=["subject"],
        )
        return jsonify([t["subject"] for t in templates if "subject" in t])
