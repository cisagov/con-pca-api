"""Utility views."""
# Standard Python Libraries
import random
import string

# Third-Party Libraries
from flask import jsonify, render_template, render_template_string, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CustomerManager
from api.phish import get_tracking_info
from utils.emails import Email, get_email_context, get_from_address
from utils.images import base64_encode_image, reduce_image_size

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
                data["smtp"], "test", "test", {"name": "test"}
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


class ImageEncodeView(MethodView):
    """ImageEncodeView."""

    def post(self):
        """Return base64 encode of an image file."""
        # Get file from request
        file = request.files["file"]

        # Decrease image size
        img = reduce_image_size(file.stream, file.content_type)

        # Base 64 encode and return image
        base64_encode = base64_encode_image(img)

        # Return result
        result = {"imageUrl": f"data:image/jpeg;base64,{base64_encode.decode()}"}
        return jsonify(result), 200


class RandomPasswordView(MethodView):
    """RandomPasswordView."""

    def get(self):
        """Get a randomly generated password."""
        length = 20
        characters = (
            string.ascii_lowercase
            + string.ascii_uppercase
            + string.digits
            + string.punctuation
        )
        password = "".join(random.sample(characters, length))
        return jsonify({"password": password})
