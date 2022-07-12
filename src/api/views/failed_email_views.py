"""Failed Email views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import FailedEmailManager, SubscriptionManager, TargetManager
from utils.logging import setLogger

logger = setLogger(__name__)

failed_email_manager = FailedEmailManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()


class FailedEmailsView(MethodView):
    """FailedEmailsView."""

    def get(self):
        """Get."""
        # Allow querying a list of failed emails
        parameters = failed_email_manager.get_query(request.args)
        parameters["removed"] = {"$in": [False, None]}
        if request.args.get("removed", "").lower() == "true":
            parameters["removed"] = True

        return jsonify(failed_email_manager.all(params=parameters))


class FailedEmailView(MethodView):
    """FailedEmailView."""

    def delete(self, failed_email_id):
        """Delete."""
        failed_email = failed_email_manager.get(document_id=failed_email_id)
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
                failed_email["removed"] = True
            except Exception as e:
                logger.exception(e)
                failed_email["removed"] = False
        failed_email_manager.update(
            document_id=failed_email_id,
            data=failed_email,
        )
        return jsonify({"success": True})
