"""Sending Profile views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import (
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TemplateManager,
)
from utils.notifications import Notification
from utils.stats import get_sending_profile_metrics

sending_profile_manager = SendingProfileManager()
template_manager = TemplateManager()
subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()


class SendingProfilesView(MethodView):
    """SendingProfilesView."""

    def get(self):
        """Get."""
        parameters = sending_profile_manager.get_query(request.args)
        sending_profiles = sending_profile_manager.all(params=parameters)
        get_sending_profile_metrics(subscription_manager.all(), sending_profiles)
        return jsonify(sending_profiles)

    def post(self):
        """Post."""
        unique_emails = []
        for subscription in subscription_manager.all():
            if subscription["primary_contact"]["email"] not in unique_emails:
                unique_emails.append(subscription["primary_contact"]["email"])  # test
                Notification(
                    "domain_added_notice",
                    subscription=subscription,
                    cycle=cycle_manager.get(filter_data={"active": True}),
                    new_domain=request.json["from_address"].split("@")[1],
                ).send()
        return jsonify(sending_profile_manager.save(request.json))


class SendingProfileView(MethodView):
    """SendingProfileView."""

    def get(self, sending_profile_id):
        """Get."""
        return jsonify(sending_profile_manager.get(document_id=sending_profile_id))

    def put(self, sending_profile_id):
        """Put."""
        sending_profile_manager.update(
            document_id=sending_profile_id, data=request.json
        )
        return jsonify({"success": True})

    def delete(self, sending_profile_id):
        """Delete."""
        templates = template_manager.all(
            params={"sending_profile_id": sending_profile_id},
            fields=["template_id", "name"],
        )
        if templates:
            return (
                jsonify(
                    {
                        "error": "Templates are utilizing this sending profile.",
                        "templates": templates,
                    }
                ),
                400,
            )

        subscriptions = subscription_manager.all(
            params={"sending_profile_id": sending_profile_id},
            fields=["_id", "name"],
        )
        if subscriptions:
            return (
                jsonify(
                    {
                        "error": "Subscriptions currently assigned this sending profile.",
                        "subscriptions": subscriptions,
                    }
                ),
                400,
            )
        sending_profile_manager.delete(document_id=sending_profile_id)
        return jsonify({"success": True})
