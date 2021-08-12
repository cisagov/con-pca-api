"""Utility views."""
# Third-Party Libraries
from flask import render_template, request
from flask.views import MethodView
from utils.emails import send_email


class TestEmailView(MethodView):
    """TestEmailView."""

    def post(self):
        """Post."""
        data = request.json
        email_body = render_template("emails/test.html")
        send_email(
            to_email=data["email"],
            from_email=data["smtp"]["from_address"],
            subject="test",
            body=email_body,
            sending_profile=data["smtp"],
        )
