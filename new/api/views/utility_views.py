"""Utility views."""
# Third-Party Libraries
from flask import jsonify, render_template, render_template_string, request
from flask.views import MethodView
from utils.emails import get_email_context, get_from_address, send_email

# cisagov Libraries
from api.manager import CustomerManager

customer_manager = CustomerManager()


class TestEmailView(MethodView):
    """TestEmailView."""

    def post(self):
        """Post."""
        data = request.json

        if data.get("template"):
            customer = customer_manager.get(uuid=data["customer_uuid"])
            target = {
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "position": data["position"],
            }
            template = data["template"]
            context = get_email_context(customer=customer, target=target)
            email_body = render_template_string(template["html"], **context)
            from_address = get_from_address(data["smtp"], template["from_address"])
            send_email(
                to_email=data["email"],
                from_email=from_address,
                subject=template["subject"],
                body=email_body,
                sending_profile=data["smtp"],
            )
        else:
            context = get_email_context()
            email_body = render_template("emails/test.html", **context)
            send_email(
                to_email=data["email"],
                from_email=data["smtp"]["from_address"],
                subject="test",
                body=email_body,
                sending_profile=data["smtp"],
            )
        return jsonify({"success": True}), 200
