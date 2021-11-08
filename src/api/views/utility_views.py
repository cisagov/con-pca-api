"""Utility views."""
# Third-Party Libraries
from flask import jsonify, render_template, render_template_string, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CustomerManager
from api.phish import get_tracking_info
from utils.emails import Email, get_email_context, get_from_address

customer_manager = CustomerManager()


class TestEmailView(MethodView):
    """TestEmailView."""

    def post(self):
        """Post."""
        data = request.json

        email = Email(data["smtp"])
        if data.get("template"):
            customer = customer_manager.get(document_id=data["customer_id"])
            target = {
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "position": data["position"],
            }
            template = data["template"]
            tracking_info = get_tracking_info(
                data["smtp"],
                "test",
                "test",
            )
            context = get_email_context(
                customer=customer,
                target=target,
                url=tracking_info["click"],
            )
            email_body = render_template_string(template["html"], **context)
            from_address = render_template_string(
                get_from_address(data["smtp"], template["from_address"]), **context
            )
            subject = render_template_string(template["subject"], **context)
            try:
                email.send(
                    to_recipients=[data["email"]],
                    from_email=from_address,
                    subject=subject,
                    body=email_body,
                )
            except Exception as e:
                return jsonify(str(e)), 400
        else:
            context = get_email_context()
            email_body = render_template("emails/test.html", **context)
            try:
                email.send(
                    to_recipients=[data["email"]],
                    from_email=data["smtp"]["from_address"],
                    subject="test",
                    body=email_body,
                )
            except Exception as e:
                return jsonify(str(e)), 400
        return jsonify({"success": True}), 200
