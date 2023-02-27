"""Notification Views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import (
    CycleManager,
    NotificationManager,
    SendingProfileManager,
    SubscriptionManager,
)
from utils.emails import parse_email

notification_manager = NotificationManager()
sp_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()


class NotificationsView(MethodView):
    """NotificationsView."""

    def get(self):
        """Get."""
        # Allow querying a list of notifications
        parameters = notification_manager.get_query(request.args)
        ids = request.args.get("ids")
        if ids:
            parameters["_id"] = {"$in": ids.split(",")}

        parameters["retired"] = {"$in": [False, None]}
        if request.args.get("retired", "").lower() == "true":
            parameters["retired"] = True

        notifications = []
        for notification in notification_manager.all(
            params=parameters,
            fields=[
                "name",
                "task_name",
                "retired",
                "retired_description",
                "subject",
                "text",
                "html",
                "created",
                "created_by",
                "updated",
                "updated_by",
            ],
        ):
            notifications.append(notification)
        return jsonify(notifications)

    def post(self):
        """Post."""
        return jsonify(notification_manager.save(request.json))


class NotificationView(MethodView):
    """NotificationView."""

    def get(self, template_id):
        """Get."""
        return jsonify(
            notification_manager.get(
                document_id=template_id,
                fields=[
                    "name",
                    "task_name",
                    "retired",
                    "retired_description",
                    "subject",
                    "text",
                    "html",
                    "created",
                    "created_by",
                    "updated",
                    "updated_by",
                ],
            )
        )

    def put(self, notification_id):
        """Put."""
        data = request.json
        notification = notification_manager.get(document_id=notification_id)
        notification.update(data)
        notification_manager.update(document_id=notification_id, data=notification)
        return jsonify({"success": True})

    def delete(self, notification_id):
        """Delete."""
        notification = notification_manager.get(document_id=notification_id)

        if not notification.get("retired"):
            return jsonify({"error": "You must retire the notification first."}), 400

        subscriptions = subscription_manager.all(
            params={"tasks.task_type": notification["task_name"]},
            fields=["_id", "name", "tasks"],
        )
        if subscriptions:
            return (
                jsonify(
                    {
                        "error": "Subscriptions are currently utilizing this notification.",
                        "subscriptions": subscriptions,
                    }
                ),
                400,
            )

        notification_manager.delete(document_id=notification_id)
        return jsonify({"success": True})


class NotificationImportView(MethodView):
    """NotificationImportView."""

    def post(self):
        """Post."""
        # TODO: Support email files
        payload = request.json["content"]
        convert_links = request.json["convert_link"]
        subject, html, text = parse_email(payload, convert_links)
        return jsonify({"subject": subject, "html": html, "text": text})


class NotificationDuplicateView(MethodView):
    """Duplicate an existing Notification."""

    def get(self, notification_id):
        """Get."""
        notification = notification_manager.get(document_id=notification_id)
        notification["name"] = f"{notification['name']} COPY"

        return jsonify(notification_manager.save(notification))
