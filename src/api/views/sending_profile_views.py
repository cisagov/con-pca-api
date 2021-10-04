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

sending_profile_manager = SendingProfileManager()
template_manager = TemplateManager()
subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()


class SendingProfilesView(MethodView):
    """SendingProfilesView."""

    def get(self):
        """Get."""
        parameters = sending_profile_manager.get_query(request.args)
        return jsonify(sending_profile_manager.all(params=parameters))

    def post(self):
        """Post."""
        return jsonify(sending_profile_manager.save(request.json))


class SendingProfileView(MethodView):
    """SendingProfileView."""

    def get(self, sending_profile_uuid):
        """Get."""
        return jsonify(sending_profile_manager.get(uuid=sending_profile_uuid))

    def put(self, sending_profile_uuid):
        """Put."""
        sending_profile_manager.update(uuid=sending_profile_uuid, data=request.json)
        return jsonify({"success": True})

    def delete(self, sending_profile_uuid):
        """Delete."""
        templates = template_manager.all(
            params={"sending_profile_uuid": sending_profile_uuid},
            fields=["template_uuid", "name"],
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
            params={"sending_profile_uuid": sending_profile_uuid},
            fields=["subscription_uuid", "name"],
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
        return jsonify(sending_profile_manager.delete(uuid=sending_profile_uuid))