"""Subscription Views."""
# Standard Python Libraries
from collections import OrderedDict
from datetime import datetime, timedelta
import os

# Third-Party Libraries
from bson.objectid import ObjectId
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
from utils.templates import get_random_templates
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

        if request.args.get("customer_id", None):
            match = {
                "$match": {
                    "$and": [
                        {"archived": {"$in": [False, None]}},
                        {"customer_id": request.args.get("customer_id")},
                    ]
                }
                if not parameters["archived"]
                else {
                    "$and": [
                        {"archived": {"$nin": [False, None]}},
                        {"customer_id": request.args.get("customer_id")},
                    ]
                }
            }
        else:
            match = {
                "$match": {"archived": {"$in": [False, None]}}
                if not parameters["archived"]
                else {"archived": {"$nin": [False, None]}}
            }

        pipeline = [
            match,
            {
                "$addFields": {
                    "subscription_id": {"$toString": "$_id"},
                    "customer_object_id": {"$toObjectId": "$customer_id"},
                }
            },
            {
                "$lookup": {
                    "from": "cycle",
                    "localField": "subscription_id",
                    "foreignField": "subscription_id",
                    "as": "cycle",
                }
            },
            {
                "$lookup": {
                    "from": "customer",
                    "localField": "customer_object_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
            {
                "$project": {
                    "_id": "$_id",
                    "appendix_a_date": {"$max": "$customer.appendix_a_date"},
                    "cycle_start_date": {"$max": "$cycle.start_date"},
                    "created": "$created",
                    "target_domain": "$target_domain",
                    "customer_id": "$customer_id",
                    "name": "$name",
                    "status": "$status",
                    "start_date": "$start_date",
                    "cycle_length_minutes": "$cycle_length_minutes",
                    "cooldown_minutes": "$cooldown_minutes",
                    "buffer_time_minutes": "$buffer_time_minutes",
                    "active": {"$anyElementTrue": "$cycle.active"},
                    "archived": "$archived",
                    "primary_contact": "$primary_contact",
                    "admin_email": "$admin_email",
                    "target_email_list": "$target_email_list",
                    "continuous_subscription": "$continuous_subscription",
                    "targets_updated_username": "$targets_updated_username",
                    "targets_updated_time": "$targets_updated_time",
                    "created_by": "$created_by",
                    "updated": "$updated",
                    "updated_by": "$updated_by",
                    "processing": "$processing",
                }
            },
            {"$sort": {"subscription.name": 1}},
        ]
        subscriptions = subscription_manager.aggregate(pipeline)
        for subscription in subscriptions:
            subscription["_id"] = str(subscription["_id"])

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


class SubscriptionsPagedView(MethodView):
    """Subscriptions Paged View."""

    def get(self, page, pagesize, sortby, sortorder):
        """Get."""
        parameters = dict(request.args)
        parameters = subscription_manager.get_query(parameters)

        sortdirection = 1
        if sortorder == "desc":
            sortdirection = -1

        sort_dict = OrderedDict()
        if sortby != "name":
            sort_dict[sortby] = sortdirection
            sort_dict["name_no_inc"] = 1
            sort_dict["created"] = 1
        else:
            sort_dict["name_no_inc"] = sortdirection
            sort_dict["created"] = sortdirection

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

        if "archived" in request.args:
            archived = [
                # { "archived": True  },
                {"archived": True},
            ]
        else:
            archived = [{"archived": {"$exists": False}}, {"archived": False}]

        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        compareDate = datetime.now()
        compareDate += timedelta(days=1)

        pipeline = [
            {
                "$addFields": {
                    "subscription_id": {"$toString": "$_id"},
                    "customer_object_id": {"$toObjectId": "$customer_id"},
                    "contact_full_name": {
                        "$concat": [
                            "$primary_contact.first_name",
                            " ",
                            "$primary_contact.last_name",
                        ]
                    },
                    "name_inc": {"$last": {"$split": ["$name", "_"]}},
                    "name_no_inc": {"$first": {"$split": ["$name", "_"]}},
                    "target_count": {"$size": "$target_email_list"},
                },
            },
            {
                "$lookup": {
                    "from": "customer",
                    "localField": "customer_object_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
            {
                "$lookup": {
                    "from": "cycle",
                    "let": {"subscription_id": "$subscription_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$and": [
                                    {
                                        "start_date": {"$lte": compareDate},
                                    },
                                    {
                                        "$expr": {
                                            "$eq": [
                                                "$subscription_id",
                                                "$$subscription_id",
                                            ]
                                        }
                                    },
                                ]
                            }
                        }
                    ],
                    "as": "cycle",
                }
            },
            {"$sort": sort_dict},
            {"$skip": int(page) * int(pagesize)},
            {"$limit": int(pagesize)},
            {
                "$project": {
                    "_id": "$_id",
                    "appendix_a_date": {"$max": "$customer.appendix_a_date"},
                    "cycle_start_date": {"$max": "$cycle.start_date"},
                    "created": "$created",
                    "target_domain": "$target_domain",
                    "customer_id": "$customer_id",
                    "name": "$name",
                    "status": "$status",
                    "start_date": "$start_date",
                    "cycle_length_minutes": "$cycle_length_minutes",
                    "cooldown_minutes": "$cooldown_minutes",
                    "buffer_time_minutes": "$buffer_time_minutes",
                    "active": {"$anyElementTrue": "$cycle.active"},
                    "archived": "$archived",
                    "primary_contact": "$primary_contact",
                    "admin_email": "$admin_email",
                    "target_email_list": "$target_email_list",
                    "continuous_subscription": "$continuous_subscription",
                    "created_by": "$created_by",
                    "updated": "$updated",
                    "updated_by": "$updated_by",
                }
            },
        ]

        filter_val = request.args.get("searchFilter")
        if request.args.get("searchFilter"):
            filter_val = request.args.get("searchFilter")
            pipeline.insert(
                2,
                {
                    "$match": {
                        "$and": [
                            {
                                "$or": [
                                    {"name": {"$regex": filter_val, "$options": "i"}},
                                    {"status": {"$regex": filter_val, "$options": "i"}},
                                    {
                                        "primary_contact.first_name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "primary_contact.last_name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "contact_full_name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "target_domain": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "customer.name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                ]
                            },
                            {"$or": archived},
                        ]
                    }
                },
            )
        else:
            pipeline.insert(
                2,
                {"$match": {"$or": archived}},
            )

        subscriptions = subscription_manager.page(
            params=pipeline,
        )

        return jsonify(subscriptions)


class SubscriptionCountView(MethodView):
    """SubscriptionCountView."""

    def get(self):
        """Get the count of subscriptions."""
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

        if "archived" in request.args:
            archived = [
                # { "archived": True  },
                {"archived": True},
            ]
        else:
            archived = [{"archived": {"$exists": False}}, {"archived": False}]

        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        compareDate = datetime.now()
        compareDate += timedelta(days=1)

        pipeline = [
            {
                "$addFields": {
                    "subscription_id": {"$toString": "$_id"},
                    "customer_object_id": {"$toObjectId": "$customer_id"},
                    "contact_full_name": {
                        "$concat": [
                            "$primary_contact.first_name",
                            " ",
                            "$primary_contact.last_name",
                        ]
                    },
                    "name_inc": {"$last": {"$split": ["$name", "_"]}},
                    "name_no_inc": {"$first": {"$split": ["$name", "_"]}},
                    "target_count": {"$size": "$target_email_list"},
                },
            },
            {
                "$lookup": {
                    "from": "customer",
                    "localField": "customer_object_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
        ]

        filter_val = request.args.get("searchFilter")
        if request.args.get("searchFilter"):
            filter_val = request.args.get("searchFilter")
            pipeline.insert(
                2,
                {
                    "$match": {
                        "$and": [
                            {
                                "$or": [
                                    {"name": {"$regex": filter_val, "$options": "i"}},
                                    {"status": {"$regex": filter_val, "$options": "i"}},
                                    {
                                        "primary_contact.first_name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "primary_contact.last_name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "contact_full_name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "target_domain": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "customer.name": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                ]
                            },
                            {"$or": archived},
                        ]
                    }
                },
            )
        else:
            pipeline.insert(
                2,
                {"$match": {"$or": archived}},
            )

        subscriptionCount = len(
            subscription_manager.page(
                params=pipeline,
            )
        )

        return str(subscriptionCount)


class SubscriptionView(MethodView):
    """SubscriptionView."""

    def get(self, subscription_id):
        """Get."""
        pipeline = [
            {"$match": {"_id": ObjectId(subscription_id)}},
            {
                "$addFields": {
                    "subscription_id": {"$toString": "$_id"},
                    "customer_object_id": {"$toObjectId": "$customer_id"},
                }
            },
            {
                "$lookup": {
                    "from": "cycle",
                    "localField": "subscription_id",
                    "foreignField": "subscription_id",
                    "as": "cycle",
                }
            },
            {
                "$lookup": {
                    "from": "customer",
                    "localField": "customer_object_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
            {
                "$project": {
                    "_id": "$_id",
                    "name": "$name",
                    "customer_id": "$customer_id",
                    "sending_profile_id": "$sending_profile_id",
                    "target_domain": "$target_domain",
                    "start_date": "$start_date",
                    "cycle_start_date": {"$max": "$cycle.start_date"},
                    "appendix_a_date": {"$max": "$customer.appendix_a_date"},
                    "primary_contact": "$primary_contact",
                    "admin_email": "$admin_email",
                    "operator_email": "$operator_email",
                    "status": "$status",
                    "target_email_list": "$target_email_list",
                    "templates_selected": "$templates_selected",
                    "next_templates": "$next_templates",
                    "active": {"$anyElementTrue": "$cycle.active"},
                    "continuous_subscription": "$continuous_subscription",
                    "cycle_length_minutes": "$cycle_length_minutes",
                    "cooldown_minutes": "$cooldown_minutes",
                    "buffer_time_minutes": "$buffer_time_minutes",
                    "report_frequency_minutes": "$report_frequency_minutes",
                    "archived": "$archived",
                    "tasks": "$tasks",
                    "notification_history": "$notification_history",
                    "phish_header": "$phish_header",
                    "reporting_password": "$reporting_password",
                    "test_results": "$test_results",
                    "landing_page_id": "$landing_page_id",
                    "landing_page_url": "$landing_page_url",
                    "landing_domain": "$landing_domain",
                    "targets_updated_username": "$targets_updated_username",
                    "targets_updated_time": "$targets_updated_time",
                    "created": "$created",
                    "created_by": "$created_by",
                    "updated": "$updated",
                    "updated_by": "$updated_by",
                    "processing": "$processing",
                }
            },
        ]
        subscription = subscription_manager.aggregate(pipeline)
        subscription = subscription[0] if len(subscription) > 0 else {}
        subscription["_id"] = str(subscription["_id"])
        subscription["cycle_send_by_date"] = (
            subscription.get("cycle_start_date")
            + timedelta(minutes=(subscription.get("cycle_length_minutes", 0)))
            if subscription.get("cycle_start_date", None)
            else None
        )
        subscription["cycle_end_date"] = (
            subscription.get("cycle_start_date")
            + timedelta(
                minutes=(
                    subscription.get("cycle_length_minutes", 0)
                    + subscription.get("cooldown_minutes", 0)
                )
            )
            if subscription.get("cycle_start_date", None)
            else None
        )
        subscription["next_cycle_start_date"] = (
            subscription.get("cycle_start_date")
            + timedelta(
                minutes=(
                    subscription.get("cycle_length_minutes", 0)
                    + subscription.get("cooldown_minutes", 0)
                    + subscription.get("buffer_time_minutes", 0)
                )
            )
            if subscription.get("cycle_start_date", None)
            else None
        )
        return jsonify(subscription)

    def put(self, subscription_id):
        """Put."""
        subscription = subscription_manager.get(
            document_id=subscription_id,
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
        pipeline = [
            {"$match": {"archived": {"$in": [False, None]}}},
            {
                "$addFields": {
                    "subscription_id": {"$toString": "$_id"},
                    "customer_object_id": {"$toObjectId": "$customer_id"},
                }
            },
            {
                "$lookup": {
                    "from": "cycle",
                    "localField": "subscription_id",
                    "foreignField": "subscription_id",
                    "as": "cycle",
                }
            },
            {
                "$lookup": {
                    "from": "customer",
                    "localField": "customer_object_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
            {
                "$project": {
                    "_id": "$_id",
                    "appendix_a_date": {"$max": "$customer.appendix_a_date"},
                    "cycle_start_date": {"$max": "$cycle.start_date"},
                    "cycle_end_date": {"$max": "$cycle.end_date"},
                    "active": {"$anyElementTrue": "$cycle.active"},
                    "created": "$created",
                    "target_domain": "$target_domain",
                    "customer_id": "$customer_id",
                    "name": "$name",
                    "status": "$status",
                    "start_date": "$start_date",
                    "cycle_length_minutes": "$cycle_length_minutes",
                    "cooldown_minutes": "$cooldown_minutes",
                    "buffer_time_minutes": "$buffer_time_minutes",
                    "archived": "$archived",
                    "primary_contact": "$primary_contact",
                    "admin_email": "$admin_email",
                    "target_email_list": "$target_email_list",
                    "continuous_subscription": "$continuous_subscription",
                    "created_by": "$created_by",
                    "updated": "$updated",
                    "updated_by": "$updated_by",
                }
            },
        ]
        subscriptions = subscription_manager.aggregate(pipeline)
        for subscription in subscriptions:
            subscription["_id"] = str(subscription["_id"])

        return jsonify(subscriptions)


class SubscriptionLaunchView(MethodView):
    """SubscriptionLaunchView."""

    def get(self, subscription_id):
        """Launch a subscription."""
        subscription = subscription_manager.get(
            document_id=subscription_id, fields=["next_templates"]
        )
        resp, status_code = start_subscription(
            subscription_id, subscription.get("next_templates", [])
        )
        return jsonify(resp), status_code

    def delete(self, subscription_id):
        """Stop a subscription."""
        return jsonify(stop_subscription(subscription_id))


class SubscriptionTestView(MethodView):
    """SubscriptionTestView."""

    def get(self, subscription_id):
        """Get test results for a subscription."""
        parameters = dict(request.args)
        parameters["next"] = False
        if request.args.get("next", "").lower() == "true":
            parameters["next"] = True
        if parameters["next"]:
            return jsonify(
                subscription_manager.get(
                    document_id=subscription_id, fields=["next_test_results"]
                ).get("next_test_results", [])
            )
        else:
            return jsonify(
                subscription_manager.get(
                    document_id=subscription_id, fields=["test_results"]
                ).get("test_results", [])
            )

    def post(self, subscription_id):
        """Launch a test for the subscription."""
        parameters = dict(request.args)
        parameters["next"] = False
        if request.args.get("next", "").lower() == "true":
            parameters["next"] = True
        if parameters["next"]:
            resp, status_code = test_subscription(
                subscription_id, request.json["contacts"], next=True
            )
        else:
            resp, status_code = test_subscription(
                subscription_id, request.json["contacts"]
            )
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
            update_data["next_templates"] = get_random_templates(subscription)
            subscription_manager.update(document_id=subscription_id, data=update_data)

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
            next_templates_selected = get_random_templates(subscription)
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


class SubscriptionResetProcessingStateView(MethodView):
    """Manually set the subscriptions processing back to false if it gets stuck."""

    def delete(self, subscription_id):
        """Return subscription to the false processing state."""
        subscription_manager.update(
            document_id=subscription_id,
            data={
                "processing": False,
            },
        )
        return jsonify(
            subscription_manager.get(
                document_id=subscription_id,
                fields=[
                    "name",
                    "customer_id",
                    "sending_profile_id",
                    "target_domain",
                    "customer",
                    "start_date",
                    "primary_contact",
                    "admin_email",
                    "operator_email",
                    "status",
                    "cycle_start_date",
                    "target_email_list",
                    "templates_selected",
                    "next_templates",
                    "continuous_subscription",
                    "buffer_time_minutes",
                    "cycle_length_minutes",
                    "cooldown_minutes",
                    "report_frequency_minutes",
                    "tasks",
                    "processing",
                    "archived",
                    "page",
                    "page_count",
                    "sortby",
                    "sortorder",
                    "notification_history",
                    "phish_header",
                    "reporting_password",
                    "test_results",
                    "landing_page_id",
                    "landing_domain",
                    "landing_page_url",
                    "created",
                    "created_by",
                    "updated",
                    "updated_by",
                ],
            )
        )
