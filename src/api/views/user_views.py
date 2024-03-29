"""User views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from api.manager import SubscriptionManager, UserManager
from utils.aws import Cognito

cognito = Cognito()
subscription_manager = SubscriptionManager()
user_manager = UserManager()


class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get."""
        users = cognito.list_users()
        users = [
            dict(
                user,
                **{
                    "last_login": user_manager.get(
                        filter_data={"username": user.get("username", "")}
                    ).get("last_login")
                    if user_manager.get(
                        filter_data={"username": user.get("username", "")}
                    )
                    else ""
                }
            )
            for user in users
        ]
        return jsonify(users)


class UserView(MethodView):
    """UserView."""

    def delete(self, username):
        """Delete."""
        users = cognito.list_users()
        user = next(filter(lambda x: x["username"] == username, users), None)
        if not user:
            return jsonify({"error": "User does not exist."}), 400

        subscriptions = subscription_manager.all(
            {"admin_email": user["email"]}, fields=["_id", "name"]
        )
        if subscriptions:
            return (
                jsonify(
                    {
                        "error": "This user is assigned to active subscription.",
                        "subscriptions": subscriptions,
                    }
                ),
                400,
            )
        return jsonify(cognito.delete_user(username))


class UserConfirmView(MethodView):
    """UserConfirmView."""

    def get(self, username):
        """Get."""
        return jsonify(cognito.confirm_user(username))
