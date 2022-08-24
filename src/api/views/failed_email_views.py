"""Failed Email views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import FailedEmailManager, SubscriptionManager, TargetManager
from utils.logging import setLogger
from utils.mailgun import get_failed_email_events

logger = setLogger(__name__)

failed_email_manager = FailedEmailManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()


class FailedEmailsView(MethodView):
    """FailedEmailsView."""

    def get(self):
        """Get."""
        success = get_failed_email_events()
        # Allow querying a list of failed emails
        parameters = failed_email_manager.get_query(request.args)
        parameters["removed"] = {"$in": [False, None]}
        if request.args.get("removed", "").lower() == "true":
            parameters["removed"] = True
        success["failed_emails"] = failed_email_manager.all(params=parameters)
        return jsonify(success)


class FailedEmailView(MethodView):
    """FailedEmailView."""

    def delete(self, failed_email_id):
        """Delete."""
        failed_email = failed_email_manager.get(document_id=failed_email_id)
        failed_email["removed"] = True
        subscriptions = subscription_manager.all(
            params={
                "target_email_list": {
                    "$elemMatch": {
                        "email": failed_email["recipient"],
                    }
                },
            }
        )
        for subscription in subscriptions:
            try:
                target = next(
                    (
                        target
                        for target in subscription["target_email_list"]
                        if target["email"] == failed_email["recipient"]
                    ),
                    None,
                )
                subscription_manager.delete_from_list(
                    document_id=subscription["_id"],
                    field="target_email_list",
                    data=target,
                )
            except Exception as e:
                logger.exception(e)
                failed_email["removed"] = False
        failed_email_manager.update(
            document_id=failed_email_id,
            data=failed_email,
        )
        return jsonify({"success": True})
