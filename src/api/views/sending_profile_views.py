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
        resp = sending_profile_manager.delete(document_id=sending_profile_id)
        print(resp)
        return jsonify(resp)
