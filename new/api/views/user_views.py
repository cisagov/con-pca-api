"""User views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView
from utils.aws import Cognito

cognito = Cognito()


class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get."""
        return jsonify(cognito.list_users())


class UserView(MethodView):
    """UserView."""

    def delete(self, username):
        """Delete."""
        return jsonify(cognito.delete_user(username))


class UserConfirmView(MethodView):
    """UserConfirmView."""

    def get(self, username):
        """Get."""
        return jsonify(cognito.confirm_user(username))
